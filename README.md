# Agent Skills

A collection of skills for web scraping, data extraction, financial research, and source code analysis.

## Available Skills

### web-search

Search the web via DuckDuckGo. Returns Markdown-formatted results (title + snippet + URL). Supports text and news search with region filtering.

**Features:** text search, news search, region bias, no API key needed.

```bash
npx skills add https://github.com/kohoj/skills --skill web-search
```

### market-data

Query financial market data from Yahoo Finance. 8 subcommands: quote, history, fundamentals, earnings, profile, dividends, options, compare. Works with any ticker — US, HK, A-shares, crypto, forex, ETFs.

**Features:** real-time prices, OHLCV history, valuation metrics, earnings dates, options chains, dividend history, multi-ticker comparison.

```bash
npx skills add https://github.com/kohoj/skills --skill market-data
```

### twitter-scraper

Bulk-fetch tweets from any X/Twitter user via browser CDP protocol. Extracts auth from your logged-in browser, then calls the Twitter GraphQL API directly for fast, complete collection.

**Features:** date-range filtering, long-form tweet support, Twitter Articles extraction, JSON + Markdown output, cross-platform (macOS / Linux / Windows).

```bash
npx skills add https://github.com/kohoj/skills --skill twitter-scraper
```

### xiaohongshu-to-markdown

Convert Xiaohongshu (Little Red Book) image-based posts into readable Markdown. Downloads all carousel images and OCRs them into clean text using macOS Vision Framework.

**Features:** automatic HD image downloading, high-accuracy Chinese/English OCR, clean Markdown output. macOS only.

```bash
npx skills add https://github.com/kohoj/skills --skill xiaohongshu-to-markdown
```

### claude-code-dissect

Navigate and extract reusable design patterns from the Claude Code source code. Covers 9 subsystems: bootstrap, conversation engine, context compaction, tool system, permissions, hooks, multi-agent/swarm, memory, and extensions (MCP/plugins/skills/UI). Routes to the right reference file by topic, reads actual source, and returns extractable patterns with architecture diagrams.

**Features:** 9 reference files covering every major subsystem, auto-discovery of source root, precise reading orders with line numbers, cross-referenced neighbor links, structured output format.

**Requires:** Claude Code source extracted from sourcemap (see skill setup instructions).

```bash
npx skills add https://github.com/kohoj/skills --skill claude-code-dissect
```

### hermes-agent-dissect

Navigate and extract reusable design patterns from the Hermes Agent source code. Covers 10 subsystems: bootstrap/CLI, conversation engine, prompt/context, tool system, gateway (14 platform adapters), skills, terminal backends, memory/persistence, RL training environments, and integrations (ACP/MCP/plugins/delegation). Routes to the right reference file by topic, reads actual source, and returns extractable patterns with architecture diagrams.

**Features:** 10 reference files covering every major subsystem, auto-discovery of source root, precise reading orders with line numbers, cross-referenced neighbor links, structured output with design tradeoffs.

**Requires:** Hermes Agent source tree in your project.

```bash
npx skills add https://github.com/kohoj/skills --skill hermes-agent-dissect
```

## Prerequisites

- **web-search**: Python 3.11+, [uv](https://github.com/astral-sh/uv)
- **market-data**: Python 3.11+, [uv](https://github.com/astral-sh/uv)
- **twitter-scraper**: Python 3.8+, a Chromium browser with CDP enabled
- **xiaohongshu-to-markdown**: macOS, Python 3.8+, a Chromium browser with CDP enabled
- **claude-code-dissect**: Claude Code source extracted from sourcemap (no external dependencies)
- **hermes-agent-dissect**: Hermes Agent source tree in your project (no external dependencies)

## License

MIT
