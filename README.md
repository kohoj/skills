# Claude Code Skills

A collection of skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Available Skills

### x-cdp-scraper

Bulk-fetch tweets from any X/Twitter user via browser CDP protocol. Extracts auth from your logged-in browser, then calls the Twitter GraphQL API directly for fast, complete collection.

**Features:** date-range filtering, JSON + Markdown output, cross-platform (macOS / Linux / Windows).

## Installation

```bash
npx skills add https://github.com/kohoj/skills --skill x-cdp-scraper
```

## Prerequisites

- A Chromium-based browser (Chrome, Edge, Brave, Arc) logged in to X/Twitter
- Python 3.8+
- `pip install playwright httpx && playwright install chromium`

## License

MIT
