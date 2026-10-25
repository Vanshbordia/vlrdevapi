---
icon: lucide/rocket
title: Python SDK for Valorant esports data
description: API reference for VLRdevAPI - a type-safe Python SDK for Valorant esports data from VLR.gg.
---

# VLRdevAPI

A Python library for fetching data from [vlr.gg](https://www.vlr.gg/). Provides a synchronous, typed interface for accessing match listings, event data, team/player profiles, statistics, and news.

## Quick links

- [Official documentation](https://vlrdevapi.pages.dev/) - getting started, examples, and the blog
- [Tutorial guides](https://vlrdevapi.pages.dev/guides/) - step-by-step walkthroughs
- [FAQ](https://vlrdevapi.pages.dev/faq/) - install, rate limits, and data coverage
- [GitHub](https://github.com/Vanshbordia/vlrdevapi) - source code, issues, contributing
- [API Reference](api/index.md) - this site (readthedocs)

This site is the auto-generated API reference powered by Zensical + mkdocstrings. For tutorials, walkthroughs, and usage examples, visit the [official docs](https://vlrdevapi.pages.dev/).

## Installation

```bash
pip install vlrdevapi
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add vlrdevapi
```

## Highlights

- **Typed Models**: Fully validated Pydantic models for matches, series, teams, players, tournaments, and news.
- **Universal Tabular Exports**: One-line `.to_df()`, `.to_polars()`, `.to_csv()`, `.to_parquet()`, `.to_excel()`, `.to_json()`, and `.to_markdown()` on every response.
- **Model Context Protocol (MCP)**: Native `vlrdevapi-mcp` stdio server with 41 tools for Claude Desktop, Cursor, and Zed.
```


