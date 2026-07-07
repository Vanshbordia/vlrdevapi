"""Validate all Python code examples in MDX documentation.

Extracts every Python code block from official-docs/content/ (docs,
blog, guides, etc.), checks syntax validity, import resolution, then
executes examples against the live vlr.gg API.

CI/CD usage:
    python scripts/check_mdx_examples.py              # syntax + imports + run
    python scripts/check_mdx_examples.py --timeout 60  # custom per-example timeout
"""

from __future__ import annotations

import ast
import asyncio
import importlib
import io
import os
import re
import sys
import textwrap
import time
import traceback
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "official-docs" / "content"


class Result(NamedTuple):
    file: str
    code: str
    syntax_ok: bool
    syntax_error: str
    imports_ok: bool
    import_errors: list[str]
    run_ok: bool | None
    run_error: str
    duration: float


# ---------------------------------------------------------------------------
# Extractors
# ---------------------------------------------------------------------------

def extract_blocks(text: str) -> list[str]:
    return re.findall(r"(?s)```(?:python|py)[^\n]*\n(.*?)```", text)


def is_signature_block(code: str) -> bool:
    """Detect type-signature blocks like 'event.info(event_id: int) -> EventInfo'.

    Handles both single-line and multi-line signatures common in API reference
    docs where a function signature is fenced as python but is not valid code.
    """
    stripped = code.strip()
    lines = [line for line in stripped.splitlines() if line.strip() and not line.strip().startswith("#")]
    if not lines:
        return False

    # Heuristic: all significant lines must look like a function signature,
    # not like regular Python code. Look for type-annotation patterns (": type")
    # without "def", "import", "from", "await", "class", or top-level "=".

    # Quick rejection: contains real Python keywords at start
    first = lines[0].strip()
    if first.startswith(("def ", "import ", "from ", "await ", "class ", "return ", "if ", "for ", "while ", "try:", "with ")):
        return False

    # Single-line: "func(params) -> Return" or "obj.method(params) -> Return"
    if len(lines) == 1:
        return bool(re.match(
            r"^[a-zA-Z_][\w.]*\(.*\)\s*(->\s*\S+)?\s*$",
            lines[0].strip(),
        ))

    # Multi-line: check for signature structure
    # First line: "func(" or "namespace.func("
    first_stripped = first
    if not re.match(r"^[a-zA-Z_][\w.]*\($", first_stripped):
        return False

    # Middle lines: all must be indented parameters with type annotations
    # (contain ":" and end with ",") or blank/comment-only
    if len(lines) > 2:
        for line in lines[1:-1]:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if not re.match(r"^[a-zA-Z_]", stripped):
                return False
            if ":" not in stripped:
                return False

    # Last line: ")" or ") -> ReturnType"
    last = lines[-1].strip()
    if not re.match(r"^\s*\)\s*(->\s*\S+)?\s*$", last):
        return False

    return True


def normalize_code(code: str) -> str:
    """Dedent then strip a code block."""
    return textwrap.dedent(code).strip()


def all_doc_files():
    mdx_dirs = [
        DOCS_DIR / "docs",
        DOCS_DIR / "blog",
        DOCS_DIR / "guides",
    ]
    for d in mdx_dirs:
        if d.is_dir():
            for root, _dirs, files in os.walk(d):
                for f in files:
                    if f.endswith(".mdx"):
                        yield os.path.join(root, f)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_syntax(code: str) -> tuple[bool, str]:
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, str(e)


def resolve_imports(code: str) -> tuple[bool, list[str]]:
    errors: list[str] = []
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False, ["syntax error"]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                try:
                    importlib.import_module(alias.name)
                except ImportError as e:
                    errors.append(f"import {alias.name}: {e}")
        elif isinstance(node, ast.ImportFrom):
            mod_name = node.module or ""
            names = [a.name for a in node.names]
            try:
                mod = importlib.import_module(mod_name)
                for n in names:
                    if n == "*":
                        continue
                    if not hasattr(mod, n):
                        try:
                            importlib.import_module(f"{mod_name}.{n}")
                        except ImportError:
                            errors.append(f"cannot resolve {mod_name}.{n}")
            except ImportError as e:
                errors.append(f"import {mod_name}: {e}")
    return len(errors) == 0, errors


def is_runnable(code: str) -> bool:
    return ("import " in code or "from " in code) and bool(re.search(r"\w+\(", code))


def is_async(code: str) -> bool:
    return "await " in code or "async with " in code or "async for " in code or "async def " in code


async def exec_async(code: str, timeout: float) -> tuple[bool, str, float]:
    start = time.monotonic()
    namespace: dict = {"__name__": "__doc_check__"}
    has_self_contained = "asyncio.run(" in code

    try:
        if has_self_contained:
            cleaned = re.sub(
                r"asyncio\.run\(\s*(\w+)\s*\(\s*(?:,\s*)?\)\s*\)\s*",
                "await \\1()",
                code,
            )
            wrapped = "async def __example():\n" + textwrap.indent(cleaned, "    ")
        else:
            wrapped = "async def __example():\n" + textwrap.indent(code, "    ")

        compiled = compile(wrapped, "<doc_example>", "exec")
        exec(compiled, namespace)
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            coro = namespace["__example"]()
            await asyncio.wait_for(coro, timeout=timeout)
        elapsed = time.monotonic() - start
        output = out.getvalue().strip() or "(no output)"
        ok, msg = _check_output(output)
        if not ok:
            return False, msg, elapsed
        if err.getvalue().strip():
            output += "\n[stderr]\n" + err.getvalue().strip()
        return True, output, elapsed

    except asyncio.TimeoutError:
        return False, f"TIMEOUT after {time.monotonic() - start:.1f}s", time.monotonic() - start
    except Exception as e:
        tb = traceback.format_exc()
        return False, f"{type(e).__name__}: {e}\n{tb}", time.monotonic() - start


def _check_output(output: str) -> tuple[bool, str]:
    """Return (ok, message) — fails if output is empty/default."""
    stripped = output.strip()
    if not stripped or stripped == "(no output)":
        return False, "Example produced no output — all print statements were silently skipped"
    return True, stripped


async def exec_sync(code: str, timeout: float) -> tuple[bool, str, float]:
    start = time.monotonic()

    def run():
        namespace: dict = {"__name__": "__doc_check__"}
        compiled = compile(code, "<doc_example>", "exec")
        out = io.StringIO()
        err = io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            exec(compiled, namespace)
        return out.getvalue().strip() or "(no output)"

    loop = asyncio.get_running_loop()
    try:
        output = await asyncio.wait_for(
            loop.run_in_executor(None, run), timeout=timeout,
        )
        ok, msg = _check_output(output)
        if not ok:
            return False, msg, time.monotonic() - start
        return True, output, time.monotonic() - start
    except asyncio.TimeoutError:
        return False, f"TIMEOUT after {time.monotonic() - start:.1f}s", time.monotonic() - start
    except Exception as e:
        return False, f"{type(e).__name__}: {e}", time.monotonic() - start


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def has_skip_marker(code: str) -> bool:
    return any(line.strip().startswith("# doc-check: skip") for line in code.splitlines())


async def run_all(timeout: float) -> list[Result]:
    results: list[Result] = []

    print("=== Phase 1: Syntax & Import Check ===")
    for path in sorted(all_doc_files()):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        blocks = extract_blocks(text)
        rel = os.path.relpath(path, REPO_ROOT)

        for code in blocks:
            code = normalize_code(code)
            if not code:
                continue

            if is_signature_block(code):
                results.append(Result(rel, code, True, "", True, [], None, "", 0.0))
                print(f"  SKIP (signature)  {rel}")
                continue

            # Skip blocks marked with doc-check: skip (not executable, demo code, etc.)
            if has_skip_marker(code):
                results.append(Result(rel, code, True, "", True, [], None, "", 0.0))
                print(f"  SKIP (marker)  {rel}")
                continue

            syn_ok, syn_err = check_syntax(code)
            imp_ok, imp_errs = resolve_imports(code)

            if not syn_ok or not imp_ok:
                print(f"  FAIL  {rel}")
                if not syn_ok:
                    print(f"    SyntaxError: {syn_err}")
                if not imp_ok:
                    for e in imp_errs:
                        print(f"    ImportError: {e}")
                print("\n*** CHECK FAILED — aborting on first error ***")
                sys.exit(1)

            results.append(Result(rel, code, True, "", True, [], None, "", 0.0))
            print(f"  OK  {rel}")

    print(f"\n  >> Phase 1 complete: all {len(results)} block(s) OK\n")

    print(f"=== Phase 2: Live Execution ({timeout}s timeout per block) ===")
    for i, r in enumerate(results):
        code = r.code

        # Skip non-runnable blocks
        if not is_runnable(code):
            print(f"  SKIP (no function call)  {r.file}")
            continue

        # Skip user-marked blocks
        if has_skip_marker(code):
            print(f"  SKIP (marker)  {r.file}")
            continue

        if is_async(code):
            run_ok, run_msg, dur = await exec_async(code, timeout)
        else:
            run_ok, run_msg, dur = await exec_sync(code, timeout)

        results[i] = Result(r.file, r.code, r.syntax_ok, r.syntax_error, r.imports_ok, r.import_errors, run_ok, run_msg, dur)
        tag = "OK" if run_ok else "FAIL"
        print(f"  {tag} ({dur:.1f}s)  {r.file}")
        msg_short = run_msg[:200].replace("\n", "\\n")
        print(f"    -> {msg_short}")

    return results


def print_report(results: list[Result]) -> int:
    run_attempts = [r for r in results if r.run_ok is not None]
    run_oks = sum(1 for r in run_attempts if r.run_ok is True)
    run_fails = [r for r in results if r.run_ok is False]
    no_output = sum(1 for r in run_fails if "no output" in r.run_error.lower())

    print(f"\n{'='*60}")
    print(f"MDX EXAMPLES CHECK: {len(results)} code blocks, {len(run_attempts)} executed")
    print(f"  Run OK:   {run_oks}/{len(run_attempts)}")
    if no_output:
        print(f"  EMPTY OUTPUT FAILURES: {no_output} (prints were silently skipped)")
    print(f"{'='*60}")

    if run_fails:
        print(f"\nRUNTIME FAILURES ({len(run_fails)}):")
        for r in run_fails:
            tags = ""
            if "no output" in r.run_error.lower():
                tags = " [NO OUTPUT]"
            print(f"\n  {r.file}{tags}")
            print(f"  >> {r.run_error[:200]}")

    if run_fails:
        print(f"\n*** CHECK FAILED: {len(run_fails)} error(s) found ***")
        return len(run_fails)
    else:
        print("\n*** ALL CHECKS PASSED ***")
        return 0


def safe_print(text: str, **kwargs):
    """Print with fallback encoding for Unicode characters."""
    try:
        print(text, **kwargs)
    except UnicodeEncodeError:
        safe = text.encode("ascii", errors="replace").decode("ascii")
        print(safe, **kwargs)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Check MDX doc examples")
    parser.add_argument("--timeout", type=float, default=60.0, help="Per-example timeout (s)")
    parser.add_argument("--log", type=str, default="", help="Path to save verbose output log")
    args = parser.parse_args()

    log_lines: list[str] = []

    # Override print in the check module's namespace
    import builtins
    orig_print = builtins.print
    _log_lines = log_lines

    def tee_print(*args2, **kwargs):
        text = " ".join(str(a) for a in args2)
        _log_lines.append(text)
        try:
            orig_print(*args2, **kwargs)
        except UnicodeEncodeError:
            safe = text.encode("ascii", errors="replace").decode("ascii")
            orig_print(safe, **kwargs)

    builtins.print = tee_print  # type: ignore

    try:
        results = asyncio.run(run_all(args.timeout))
        exit_code = print_report(results)
    finally:
        builtins.print = orig_print

    if args.log:
        with open(args.log, "w", encoding="utf-8") as f:
            for line in _log_lines:
                f.write(line + "\n")
        orig_print(f"\nLog saved to: {args.log}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
