#!/usr/bin/env python3
"""
Validate Python code snippets in MDX/MD files under betterdocs/content/.

Features:
- Finds all .mdx and .md files under betterdocs/content/ (configurable).
- Extracts ```python code blocks and executes them.
- Runs each snippet in an isolated subprocess with PYTHONPATH set to include src/.
- Skips obviously long-running patterns by default (configurable via CLI).
- Per-snippet timeout to prevent hangs.
- Summarizes results and exits non-zero on failures.

Usage:
  python scripts/validate_betterdocs_snippets.py [--docs-dir betterdocs/content] [--timeout 30] \
      [--skip-pattern ".*(while\s+True|time\.sleep|input\()"] [--compile-only]

Notes:
- This validator assumes code examples are self-contained and suitable to run.
- If your examples require network access, run with an adequate timeout and CI network access.
- You can mark snippets to be skipped by including a line with:  # docs-validate: skip
"""
from __future__ import annotations

import argparse
import os
import random
import re
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


# Match ```python or ```python title="..." or ```python {other attributes}
PY_CODEBLOCK_START_RE = re.compile(r'^```python(?:\s+.*)?$')
PY_CODEBLOCK_END_RE = re.compile(r'^```\s*$')
SKIP_MARKER = "# docs-validate: skip"


@dataclass
class Snippet:
    file: Path
    start_line: int  # 1-based line number where code content starts
    code: str


def find_md_files(root: Path) -> List[Path]:
    """Find all .md and .mdx files in the given directory."""
    md_files = sorted([p for p in root.rglob("*.md") if p.is_file()])
    mdx_files = sorted([p for p in root.rglob("*.mdx") if p.is_file()])
    return sorted(md_files + mdx_files)


def extract_python_codeblocks(path: Path) -> List[Snippet]:
    """Extract Python code blocks from MDX/MD files."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    snippets: List[Snippet] = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        if PY_CODEBLOCK_START_RE.match(line):
            # Check if this code block is under a signature or return value section
            # Look backwards to find the most recent heading
            is_signature_block = False
            for j in range(i - 1, max(-1, i - 20), -1):  # Look back up to 20 lines
                prev_line = lines[j].strip()
                if prev_line.startswith("## Signature") or prev_line.startswith("## Return Value"):
                    is_signature_block = True
                    break
                # Stop at another heading
                if prev_line.startswith("##"):
                    break
            
            # Start of a Python code block
            i += 1
            block_start = i + 1  # 1-based line number
            block_lines: List[str] = []
            
            # Collect lines until we hit the closing ```
            while i < n:
                curr = lines[i]
                if PY_CODEBLOCK_END_RE.match(curr):
                    # End of code block
                    break
                block_lines.append(curr)
                i += 1
            
            if block_lines:
                # Trim leading/trailing blank lines
                while block_lines and block_lines[0].strip() == "":
                    block_lines.pop(0)
                    block_start += 1
                while block_lines and block_lines[-1].strip() == "":
                    block_lines.pop()
                
                if block_lines:  # Only add if there's actual content
                    code = "\n".join(block_lines)
                    # Mark signature blocks with a special skip marker
                    if is_signature_block:
                        code = "# docs-validate: skip (signature/type block)\n" + code
                    snippets.append(Snippet(file=path, start_line=block_start, code=code))
            
            i += 1  # Move past the closing ```
            continue
        i += 1

    return snippets


def compile_only(code: str) -> Optional[Exception]:
    """Compile the code without executing it."""
    try:
        compile(code, "<snippet>", "exec")
        return None
    except Exception as e:  # noqa: BLE001 - we want to capture any compile error
        return e


def run_snippet_in_subprocess(code: str, repo_root: Path, timeout: int) -> Tuple[int, str, str]:
    """Run a code snippet in an isolated subprocess."""
    # Write to temp file to avoid shell quoting issues on Windows
    with tempfile.TemporaryDirectory() as td:
        temp_py = Path(td) / "snippet.py"
        temp_py.write_text(code, encoding="utf-8")

        # Build environment with PYTHONPATH including src/
        env = os.environ.copy()
        src_path = str((repo_root / "src").resolve())
        existing = env.get("PYTHONPATH", "")
        sep = os.pathsep
        env["PYTHONPATH"] = src_path + (sep + existing if existing else "")

        # Run python with unbuffered output
        cmd = [sys.executable, "-u", str(temp_py)]
        proc = subprocess.Popen(
            cmd,
            cwd=str(repo_root),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            out, err = proc.communicate(timeout=timeout)
            return proc.returncode, out, err
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()
            return 124, out, err + "\n[timeout] snippet exceeded timeout"


DEFAULT_SKIP_PATTERN = r"(while\s+True|time\.sleep\(|input\()"
DEFAULT_TIMEOUT = 30


def should_skip(code: str, skip_re: Optional[re.Pattern[str]]) -> bool:
    """Check if a snippet should be skipped."""
    if SKIP_MARKER in code:
        return True
    if skip_re and skip_re.search(code):
        return True
    return False


def validate_snippet(args_tuple: Tuple) -> Tuple[Snippet, bool, Optional[str]]:
    """Validate a single snippet. Returns (snippet, success, error_msg)."""
    snip, repo_root, timeout, compile_only = args_tuple
    
    if compile_only:
        err = compile_only_check(snip.code)
        if err is None:
            return (snip, True, None)
        else:
            return (snip, False, f"Compile error: {err}")
    
    rc, out, err = run_snippet_in_subprocess(snip.code, repo_root, timeout)
    if rc == 0:
        return (snip, True, None)
    elif rc == 124:
        return (snip, False, "Timed out")
    else:
        error_output = f"exit {rc}"
        if out:
            error_output += f"\nSTDOUT:\n{out}"
        if err:
            error_output += f"\nSTDERR:\n{err}"
        return (snip, False, error_output)


def compile_only_check(code: str) -> Optional[Exception]:
    """Compile the code without executing it."""
    try:
        compile(code, "<snippet>", "exec")
        return None
    except Exception as e:  # noqa: BLE001 - we want to capture any compile error
        return e


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Python code snippets in MDX/MD files")
    parser.add_argument("--docs-dir", default="betterdocs/content", help="Root docs directory to scan for MDX/MD files")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Per-snippet timeout in seconds")
    parser.add_argument("--skip-pattern", default=DEFAULT_SKIP_PATTERN, help="Regex; snippets matching are skipped")
    parser.add_argument("--compile-only", action="store_true", help="Only compile snippets, do not execute")
    parser.add_argument("--workers", type=int, default=1, help="Number of parallel workers (default: 1 for sequential execution)")
    args = parser.parse_args(list(argv) if argv is not None else None)

    repo_root = Path(__file__).resolve().parents[1]  # scripts/ is one level up from repo root
    docs_root = (repo_root / args.docs_dir).resolve()

    if not docs_root.exists():
        print(f"Docs directory not found: {docs_root}", file=sys.stderr)
        return 2

    md_files = find_md_files(docs_root)
    if not md_files:
        print("No .md or .mdx files found.")
        return 0

    skip_re = re.compile(args.skip_pattern) if args.skip_pattern else None
    
    total = 0
    skipped = 0
    failed = 0

    failures: List[Tuple[Snippet, str]] = []
    
    # Collect all snippets first
    all_snippets: List[Tuple[Snippet, Path, int]] = []  # (snippet, file, file_index)

    for file_idx, md_file in enumerate(md_files, 1):
        snippets = extract_python_codeblocks(md_file)
        for snip in snippets:
            all_snippets.append((snip, md_file, file_idx))
        
        # Add random delay between processing files to avoid rate limiting
        if file_idx < len(md_files):  # Don't wait after the last file
            time.sleep(random.uniform(2.0, 3.0))
    
    total = len(all_snippets)
    if total == 0:
        print("No Python code snippets found.")
        return 0
    
    # Separate skipped and to-validate snippets
    to_validate: List[Tuple[Snippet, Path, int]] = []
    
    for snip, md_file, file_idx in all_snippets:
        # Skip all search module files
        if "api/search" in str(md_file.relative_to(repo_root)).replace("\\", "/"):
            skipped += 1
            progress = f"[{file_idx}/{len(md_files)}]"
            print(f"SKIP {progress} {md_file.relative_to(repo_root)}:{snip.start_line} (search module)")
        elif should_skip(snip.code, skip_re):
            skipped += 1
            progress = f"[{file_idx}/{len(md_files)}]"
            print(f"SKIP {progress} {md_file.relative_to(repo_root)}:{snip.start_line}")
        else:
            to_validate.append((snip, md_file, file_idx))
    
    # Prepare validation tasks
    validation_tasks: List[Tuple] = []
    
    for snip, md_file, file_idx in to_validate:
        validation_tasks.append((snip, repo_root, args.timeout, args.compile_only))
    
    # Run validations in parallel
    if validation_tasks:
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            future_to_snippet = {executor.submit(validate_snippet, task): task for task in validation_tasks}
            
            completed_count = 0
            for future in as_completed(future_to_snippet):
                completed_count += 1
                task = future_to_snippet[future]
                snip = task[0]
                
                # Find the file for this snippet
                md_file = None
                file_idx = 0
                for s, f, idx in to_validate:
                    if s == snip:
                        md_file = f
                        file_idx = idx
                        break
                
                if md_file is None:
                    continue
                
                progress = f"[{file_idx}/{len(md_files)}]"
                
                try:
                    result_snip, success, error_msg = future.result()
                    
                    if success:
                        print(f"OK   {progress} {md_file.relative_to(repo_root)}:{result_snip.start_line}")
                    else:
                        failed += 1
                        failures.append((result_snip, error_msg or "Unknown error"))
                        print(f"FAIL {progress} {md_file.relative_to(repo_root)}:{result_snip.start_line} -> {error_msg}")
                except Exception as e:
                    failed += 1
                    error_msg = f"Validation error: {e}"
                    failures.append((snip, error_msg))
                    print(f"FAIL {progress} {md_file.relative_to(repo_root)}:{snip.start_line} -> {error_msg}")
                
                # Add random delay between validations to avoid overwhelming the site
                if completed_count < len(validation_tasks):
                    time.sleep(random.uniform(2.0, 3.0))

    print("\nSummary:")
    print(f"  Total snippets:  {total}")
    print(f"  Skipped:         {skipped}")
    print(f"  Validated:       {len(validation_tasks) if validation_tasks else 0}")
    print(f"  Passed:          {total - skipped - failed}")
    print(f"  Failed:          {failed}")

    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
