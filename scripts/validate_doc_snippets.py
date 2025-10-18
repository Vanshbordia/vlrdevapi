#!/usr/bin/env python3
"""
Validate Python code snippets in Sphinx .rst files under docs/.

Features:
- Finds all .rst files under docs/source/ (configurable).
- Extracts .. code-block:: python sections and executes them.
- Runs each snippet in an isolated subprocess with PYTHONPATH set to include src/.
- Skips obviously long-running patterns by default (configurable via CLI).
- Per-snippet timeout to prevent hangs.
- Summarizes results and exits non-zero on failures.

Usage:
  python scripts/validate_doc_snippets.py [--docs-dir docs/source] [--timeout 30] \
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
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


PY_CODEBLOCK_RE = re.compile(r"^\s*\.\.(?:\s+)?code-block::\s*python\s*$")
OPTION_LINE_RE = re.compile(r"^\s*:\w+:\s*")
SKIP_MARKER = "# docs-validate: skip"


@dataclass
class Snippet:
    file: Path
    start_line: int  # 1-based line number where code content starts
    code: str


def find_rst_files(root: Path) -> List[Path]:
    return sorted([p for p in root.rglob("*.rst") if p.is_file()])


def dedent_block(lines: List[str]) -> List[str]:
    # Compute minimal indent (ignoring blank lines)
    indents = []
    for line in lines:
        if line.strip() == "":
            continue
        indents.append(len(line) - len(line.lstrip(" ")))
    min_indent = min(indents) if indents else 0
    return [line[min_indent:] if len(line) >= min_indent else line for line in lines]


def extract_python_codeblocks(path: Path) -> List[Snippet]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    snippets: List[Snippet] = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        if PY_CODEBLOCK_RE.match(line):
            # Consume any option lines following the directive, e.g. :linenos:
            i += 1
            while i < n and (OPTION_LINE_RE.match(lines[i]) or lines[i].strip() == ""):
                i += 1
            # Now, lines from here that are indented (at least 3 spaces) belong to the code block
            block_lines: List[str] = []
            block_start = i + 1  # 1-based
            while i < n:
                curr = lines[i]
                if curr.strip() == "":
                    # Blank lines inside block are allowed but must be indented. If it's truly blank, keep and move on.
                    block_lines.append(curr)
                    i += 1
                    continue
                leading_spaces = len(curr) - len(curr.lstrip(" "))
                if leading_spaces >= 3:
                    block_lines.append(curr)
                    i += 1
                else:
                    break
            if block_lines:
                dedented = dedent_block(block_lines)
                # Trim leading/trailing blank lines
                while dedented and dedented[0].strip() == "":
                    dedented.pop(0)
                while dedented and dedented[-1].strip() == "":
                    dedented.pop()
                code = "\n".join(dedented)
                snippets.append(Snippet(file=path, start_line=block_start, code=code))
            continue  # already moved i appropriately
        i += 1

    return snippets


def compile_only(code: str) -> Optional[Exception]:
    try:
        compile(code, "<snippet>", "exec")
        return None
    except Exception as e:  # noqa: BLE001 - we want to capture any compile error
        return e


def run_snippet_in_subprocess(code: str, repo_root: Path, timeout: int) -> Tuple[int, str, str]:
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


def should_skip(code: str, skip_re: Optional[re.Pattern[str]]) -> bool:
    if SKIP_MARKER in code:
        return True
    if skip_re and skip_re.search(code):
        return True
    return False


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Python code snippets in .rst files")
    parser.add_argument("--docs-dir", default="docs/source", help="Root docs directory to scan for .rst files")
    parser.add_argument("--timeout", type=int, default=30, help="Per-snippet timeout in seconds")
    parser.add_argument("--skip-pattern", default=DEFAULT_SKIP_PATTERN, help="Regex; snippets matching are skipped")
    parser.add_argument("--compile-only", action="store_true", help="Only compile snippets, do not execute")
    args = parser.parse_args(list(argv) if argv is not None else None)

    repo_root = Path(__file__).resolve().parents[2]  # scripts/ is one level, repo root is two up
    docs_root = (repo_root / args.docs_dir).resolve()

    if not docs_root.exists():
        print(f"Docs directory not found: {docs_root}", file=sys.stderr)
        return 2

    rst_files = find_rst_files(docs_root)
    if not rst_files:
        print("No .rst files found.")
        return 0

    skip_re = re.compile(args.skip_pattern) if args.skip_pattern else None

    total = 0
    skipped = 0
    failed = 0

    failures: List[Tuple[Snippet, str]] = []

    for file_idx, rst in enumerate(rst_files, 1):
        snippets = extract_python_codeblocks(rst)
        if not snippets:
            continue
        
        # Add random delay between processing files to avoid rate limiting
        if file_idx > 1:  # Wait before processing each file except the first
            time.sleep(random.uniform(2.0, 3.0))
        
        for snip in snippets:
            total += 1
            if should_skip(snip.code, skip_re):
                skipped += 1
                print(f"SKIP {rst.relative_to(repo_root)}:{snip.start_line}")
                continue
            if args.compile_only:
                err = compile_only(snip.code)
                if err is None:
                    print(f"OK   {rst.relative_to(repo_root)}:{snip.start_line}")
                else:
                    failed += 1
                    msg = f"Compile error: {err}"
                    failures.append((snip, msg))
                    print(f"FAIL {rst.relative_to(repo_root)}:{snip.start_line} -> {msg}")
                continue

            rc, out, err = run_snippet_in_subprocess(snip.code, repo_root=repo_root, timeout=args.timeout)
            
            # Add random delay between snippet validations to avoid overwhelming the site
            time.sleep(random.uniform(2.0, 3.0))
            
            if rc == 0:
                print(f"OK   {rst.relative_to(repo_root)}:{snip.start_line}")
            elif rc == 124:
                failed += 1
                msg = "Timed out"
                failures.append((snip, msg))
                print(f"FAIL {rst.relative_to(repo_root)}:{snip.start_line} -> {msg}")
                if out:
                    sys.stdout.write(out)
                if err:
                    sys.stderr.write(err)
            else:
                failed += 1
                header = f"Failure in {rst.relative_to(repo_root)}:{snip.start_line} (exit {rc})"
                failures.append((snip, header))
                print(f"FAIL {rst.relative_to(repo_root)}:{snip.start_line} -> exit {rc}")
                if out:
                    sys.stdout.write(out)
                if err:
                    sys.stderr.write(err)

    print("\nSummary:")
    print(f"  Total snippets:  {total}")
    print(f"  Skipped:         {skipped}")
    print(f"  Passed:          {total - skipped - failed}")
    print(f"  Failed:          {failed}")

    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
