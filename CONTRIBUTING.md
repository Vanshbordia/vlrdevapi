# Contributing to vlrdevapi

Thank you for your interest in contributing!

## Development Setup

1. Clone the repo: `git clone https://github.com/Vanshbordia/vlrdevapi`
2. Install dependencies: `uv sync --group dev`
3. Run pre-checks: `ruff check src/` and `ty check src/vlrdevapi/`

## Pull Request Guidelines

- Keep PRs focused on a single concern.
- Add or update tests for any changed behavior.
- Run `ruff check src/ tests/` and `ty check src/vlrdevapi/` before pushing.
- Update the CHANGELOG.md under the next version header.
- If changing documentation (.mdx files), run `uv run scripts/check_mdx_examples.py` and ensure all checks pass.

## Code Style

- Follow PEP 8 with `ruff` defaults (120-char lines, double quotes).
- Use Google-style docstrings on all public methods.
- Annotate all function signatures with type hints.
- Use `Literal` over `Union[Literal, str]` — validation is handled at runtime.

## Project Structure

```
src/vlrdevapi/
  _base.py          # SyncNamespace base class
  _cache.py         # LRUCache
  client.py         # VLRClient
  commons/          # Shared utilities (mappings, datetime, countries)
  event/            # Event/tournament endpoints
  matches/          # Match listing endpoints (live / upcoming / completed)
  player/           # Player endpoints (info / teams / agents / matches / profile)
  series/           # Series (match detail) endpoints
  team/             # Team endpoints (info / roster / placements / etc.)
  validators.py     # Input sanitization / validation
  fetcher.py        # HTTP fetching with retries and rate limiting
```
