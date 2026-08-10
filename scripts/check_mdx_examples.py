"""Validate all Python code examples in MDX documentation.

Extracts every Python code block from official-docs/content/ (docs,
blog, guides, etc.), checks syntax validity, import resolution, then
executes examples. An ``httpx.Client.get`` interceptor de-duplicates
fetches within a run and can replay validation offline against HTML
fixtures saved under ``.cache/mdx-html/`` (gitignored).

CI/CD usage:
    python scripts/check_mdx_examples.py              # warm + offline replay
    python scripts/check_mdx_examples.py --skip-warm  # offline replay only
    python scripts/check_mdx_examples.py --live       # single live pass
    python scripts/check_mdx_examples.py --timeout 60 # custom per-example timeout
"""

from __future__ import annotations

import ast
import asyncio
import hashlib
import importlib
import io
import os
import re
import sys
import textwrap
import threading
import time
import traceback
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import NamedTuple

import httpx

from vlrdevapi.fetcher import DEFAULT_RATE_LIMIT, RateLimiter

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "official-docs" / "content"
DEFAULT_FIXTURES_DIR = REPO_ROOT / ".cache" / "mdx-html"

DYNAMIC_PATHS = frozenset({"/matches", "/matches/results", "/events", "/news"})


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
# HTTP cache (dedup + offline replay)
# ---------------------------------------------------------------------------

class HTTPCache:
    """Thread-safe HTTP response cache that intercepts ``httpx.Client.get``.

    Patched at the class level so every library request — sync, parallel
    worker threads, enrichment, and the dark-mode team info double fetch —
    funnels through it (all go via ``fetcher.fetch_sync`` ->
    ``client.get``). Keys are sha256 of the resolved URL + sorted headers,
    so the same path fetched with a different ``Cookie`` header (dark mode)
    gets a distinct cache entry.

    Modes:
        record: disk hit -> reuse (no network); miss -> live fetch + cache.
        replay: hit -> reuse; miss -> live fallback (no disk writes).
        live:   in-memory only; miss -> live fetch + memory cache.

    Time-varying listing pages (``/matches``, ``/matches/results``,
    ``/events``) are treated as dynamic: always fetched live, deduplicated
    in memory only, and never persisted to disk. Serving a stale cached
    fixture for these could silently validate examples against outdated
    match data.
    """

    def __init__(self, fixtures_dir: Path | None, mode: str) -> None:
        self.fixtures_dir = fixtures_dir
        self.mode = mode
        self._lock = threading.Lock()
        self._mem: dict[str, str] = {}
        self._orig_get = None
        self.total_requests = 0
        self.live_fetches = 0
        self.hits_mem = 0
        self.hits_disk = 0
        self.misses = 0
        self.live_fallbacks = 0
        self.unique_pages: set[str] = set()

    def install(self) -> None:
        """Patch ``httpx.Client.get`` at the class level."""
        if self._orig_get is None:
            self._orig_get = httpx.Client.get
            cache = self
            orig_get = self._orig_get

            def _intercept(client: httpx.Client, url: str, **kwargs) -> httpx.Response:
                return cache._handle(client, url, orig_get, **kwargs)

            httpx.Client.get = _intercept  # type: ignore[method-assign]

    def restore(self) -> None:
        """Restore the original ``httpx.Client.get``."""
        if self._orig_get is not None:
            httpx.Client.get = self._orig_get  # type: ignore[method-assign]
            self._orig_get = None

    def _key(self, request: httpx.Request, headers: dict[str, str] | None) -> str:
        header_items = sorted((headers or {}).items())
        payload = f"{request.url}|{header_items!r}".encode()
        return hashlib.sha256(payload).hexdigest()

    def _lookup(self, key: str, allow_disk: bool = True) -> str | None:
        with self._lock:
            html = self._mem.get(key)
            if html is not None:
                self.hits_mem += 1
                return html
            if allow_disk and self.fixtures_dir is not None:
                fixture = self.fixtures_dir / f"{key}.html"
                if fixture.exists():
                    try:
                        html = fixture.read_text(encoding="utf-8")
                    except OSError:
                        html = None
                    if html is not None:
                        self._mem[key] = html
                        self.hits_disk += 1
                        return html
            return None

    def _store(self, key: str, html: str, to_disk: bool = True) -> None:
        with self._lock:
            self._mem[key] = html
            if to_disk and self.mode == "record" and self.fixtures_dir is not None:
                try:
                    self.fixtures_dir.mkdir(parents=True, exist_ok=True)
                    fixture = self.fixtures_dir / f"{key}.html"
                    if not fixture.exists():
                        fixture.write_text(html, encoding="utf-8")
                except OSError:
                    pass

    def _throttle(self) -> None:
        if DEFAULT_RATE_LIMIT > 0:
            time.sleep(1.0 / DEFAULT_RATE_LIMIT)

    def _handle(
        self,
        client: httpx.Client,
        url: str,
        orig_get,
        **kwargs,
    ) -> httpx.Response:
        self.total_requests += 1
        headers = kwargs.get("headers")
        request = client.build_request("GET", url, headers=headers)
        key = self._key(request, headers)
        self.unique_pages.add(key)
        dynamic = request.url.path in DYNAMIC_PATHS

        cached = self._lookup(key, allow_disk=not dynamic)
        if cached is not None:
            return httpx.Response(200, text=cached, request=request)

        self.misses += 1
        if self.mode == "replay":
            self.live_fallbacks += 1
            self._throttle()
        self.live_fetches += 1
        resp = orig_get(client, url, **kwargs)
        if resp.status_code == 200 and self.mode in ("record", "live"):
            self._store(key, resp.text, to_disk=not dynamic)
        return resp


class RunStats:
    """Durations for each phase, reported in the summary footer."""

    def __init__(self) -> None:
        self.phase1 = 0.0
        self.warm = 0.0
        self.replay = 0.0


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
    return bool(re.match(r"^\s*\)\s*(->\s*\S+)?\s*$", last))


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
        exec(compiled, namespace)  # noqa: S102
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

    except TimeoutError:
        return False, f"TIMEOUT after {time.monotonic() - start:.1f}s", time.monotonic() - start
    except Exception as e:  # noqa: BLE001
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
            exec(compiled, namespace)  # noqa: S102
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
    except TimeoutError:
        return False, f"TIMEOUT after {time.monotonic() - start:.1f}s", time.monotonic() - start
    except Exception as e:  # noqa: BLE001
        return False, f"{type(e).__name__}: {e}", time.monotonic() - start


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def has_skip_marker(code: str) -> bool:
    return any(line.strip().startswith("# doc-check: skip") for line in code.splitlines())


async def execute_blocks(
    results: list[Result],
    timeout: float,
    cache: HTTPCache,
    label: str,
    *,
    record_results: bool,
) -> None:
    """Execute every runnable block against the current cache mode.

    In warm mode (``record_results=False``) execution is best-effort: the
    point is to populate the cache/fixtures and de-duplicate fetches, so
    failures do not affect the run. In replay/live mode (``record_results=True``)
    results are recorded and validated.
    """
    print(f"=== Phase: {label} ===")
    for i, r in enumerate(results):
        code = r.code

        # Skip non-runnable blocks
        if not is_runnable(code):
            continue

        # Skip user-marked blocks
        if has_skip_marker(code):
            continue

        if is_async(code):
            run_ok, run_msg, dur = await exec_async(code, timeout)
        else:
            run_ok, run_msg, dur = await exec_sync(code, timeout)

        if record_results:
            results[i] = Result(
                r.file, r.code, r.syntax_ok, r.syntax_error, r.imports_ok,
                r.import_errors, run_ok, run_msg, dur,
            )
            tag = "OK" if run_ok else "FAIL"
        else:
            tag = "warm-ok" if run_ok else "warm-err"

        print(f"  {tag} ({dur:.1f}s)  {r.file}")
        if record_results:
            msg_short = run_msg[:200].replace("\n", "\\n")
            print(f"    -> {msg_short}")


async def run_all(
    timeout: float,
    cache: HTTPCache,
    *,
    skip_warm: bool,
    live: bool,
) -> tuple[list[Result], RunStats]:
    stats = RunStats()
    results: list[Result] = []

    print("=== Phase 1: Syntax & Import Check ===")
    phase1_start = time.monotonic()
    for path in sorted(all_doc_files()):
        with open(path, encoding="utf-8") as f:  # noqa: ASYNC230
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

    stats.phase1 = time.monotonic() - phase1_start
    print(f"\n  >> Phase 1 complete: all {len(results)} block(s) OK\n")

    if live:
        cache.mode = "live"
        print(f"=== Live execution ({timeout}s timeout per block, in-memory dedup) ===")
        replay_start = time.monotonic()
        await execute_blocks(results, timeout, cache, "Live (validated)", record_results=True)
        stats.replay = time.monotonic() - replay_start
        return results, stats

    if not skip_warm:
        cache.mode = "record"
        warm_start = time.monotonic()
        await execute_blocks(results, timeout, cache, "Warm (record fixtures)", record_results=False)
        stats.warm = time.monotonic() - warm_start
        print(f"\n  >> Warm phase complete: fixtures ready in {cache.fixtures_dir}\n")

    cache.mode = "replay"
    print(f"=== Replay execution ({timeout}s timeout per block, offline against fixtures) ===")
    orig_acquire = RateLimiter.acquire
    RateLimiter.acquire = lambda self: None  # type: ignore[method-assign]
    try:
        replay_start = time.monotonic()
        await execute_blocks(results, timeout, cache, "Replay (validated)", record_results=True)
        stats.replay = time.monotonic() - replay_start
    finally:
        RateLimiter.acquire = orig_acquire  # type: ignore[method-assign]

    return results, stats


def print_report(results: list[Result], cache: HTTPCache | None = None, stats: RunStats | None = None) -> int:
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

    if cache is not None:
        saved = cache.total_requests - cache.live_fetches
        print("\nHTTP CACHE STATS:")
        print(f"  Requests intercepted: {cache.total_requests}")
        print(f"  Unique pages touched: {len(cache.unique_pages)}")
        print(f"  Live fetches:         {cache.live_fetches}  (dedup saved {max(saved, 0)})")
        print(f"  Cache hits:           {cache.hits_mem} mem / {cache.hits_disk} disk")
        print(f"  Cache misses:         {cache.misses}")
        if cache.live_fallbacks:
            print(f"  Live fallbacks:       {cache.live_fallbacks}")
    if stats is not None:
        print("\nPHASE DURATIONS:")
        print(f"  Phase 1 (static): {stats.phase1:.1f}s")
        if stats.warm:
            print(f"  Warm  (record):   {stats.warm:.1f}s")
        print(f"  Replay/validate:  {stats.replay:.1f}s")

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
    parser.add_argument(
        "--fixtures-dir", type=str, default=str(DEFAULT_FIXTURES_DIR),
        help="Directory for cached HTML fixtures (default: .cache/mdx-html)",
    )
    parser.add_argument(
        "--skip-warm", action="store_true",
        help="Skip the warm (record) phase; replay against existing fixtures",
    )
    parser.add_argument(
        "--live", action="store_true",
        help="Single live pass with in-memory dedup (no disk fixtures)",
    )
    args = parser.parse_args()

    fixtures_dir = None
    if not args.live and args.fixtures_dir:
        fixtures_dir = Path(args.fixtures_dir)
    cache = HTTPCache(fixtures_dir=fixtures_dir, mode="replay")
    stats = RunStats()

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
        cache.install()
        results, stats = asyncio.run(
            run_all(args.timeout, cache, skip_warm=args.skip_warm, live=args.live)
        )
        exit_code = print_report(results, cache=cache, stats=stats)
    finally:
        cache.restore()
        builtins.print = orig_print

    if args.log:
        with open(args.log, "w", encoding="utf-8") as f:
            f.writelines(line + "\n" for line in _log_lines)
        orig_print(f"\nLog saved to: {args.log}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
