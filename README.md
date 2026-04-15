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

### podcast-to-md

Turn any Apple Podcast into structured Markdown files with rich frontmatter, show notes, and timestamped transcripts. Supports search by name or URL, date-range filtering, automatic transcript detection from RSS feeds, and local Whisper transcription as fallback.

**Features:** iTunes search/lookup, RSS metadata extraction (iTunes + Podcasting 2.0 namespaces), time filtering, transcript URL detection, local faster-whisper transcription, structured frontmatter, index generation.

```bash
npx skills add https://github.com/kohoj/skills --skill podcast-to-md
```

### ascii-rendering

High-quality image-to-ASCII conversion using shape-vector matching. Instead of treating characters as pixels, this renderer quantifies the geometric shape of each ASCII character via 6D shape vectors and picks the best match per cell. Produces sharp edges and crisp contours.

**Features:** 6D shape-vector matching, contrast enhancement for edge sharpness, image/video/webcam input, ANSI true-color output, multiple charsets, adjustable font aspect ratio.

```bash
npx skills add https://github.com/kohoj/skills --skill ascii-rendering
```

### mogu-visual

Transform technical descriptions into interactive animated HTML visualizations starring Mogu — a mushroom character whose cap shape, texture, and color adapt to each concept. Generates self-contained HTML files with Canvas 2D animations and interactive parameter controls.

**Features:** Mogu character brand with 5 expressions, 8+ cap shapes, 8+ cap textures, 9 scene archetypes, interactive parameter controls, absorption ceremony intro animation.

```bash
npx skills add https://github.com/kohoj/skills --skill mogu-visual
```

## Prerequisites

- **web-search**: Python 3.11+, [uv](https://github.com/astral-sh/uv)
- **market-data**: Python 3.11+, [uv](https://github.com/astral-sh/uv)
- **twitter-scraper**: Python 3.8+, a Chromium browser with CDP enabled
- **xiaohongshu-to-markdown**: macOS, Python 3.8+, a Chromium browser with CDP enabled
- **claude-code-dissect**: Claude Code source extracted from sourcemap (no external dependencies)
- **hermes-agent-dissect**: Hermes Agent source tree in your project (no external dependencies)
- **podcast-to-md**: Python 3.11+, [uv](https://github.com/astral-sh/uv). Local transcription requires faster-whisper (auto-installed on first use).
- **ascii-rendering**: Python 3.9+, Pillow, NumPy. Optional: OpenCV (video/camera), SciPy (KD-tree acceleration).
- **mogu-visual**: No dependencies. Generated HTML files may optionally load GSAP or D3 from CDN.

## License

MIT
