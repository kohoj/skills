# Claude Code Skills

A collection of skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

## Available Skills

### x-cdp-scraper

Bulk-fetch tweets from any X/Twitter user via browser CDP protocol. Extracts auth from your logged-in browser, then calls the Twitter GraphQL API directly for fast, complete collection.

**Features:** date-range filtering, JSON + Markdown output, cross-platform (macOS / Linux / Windows).

### xhs-to-markdown

Convert Xiaohongshu (Little Red Book) image-based posts into readable Markdown. Extracts carousel images via CDP cookies + httpx, then OCRs them using macOS Vision Framework.

**Features:** automatic image downloading, high-accuracy Chinese/English OCR, clean Markdown output. macOS only.

## Installation

```bash
# X/Twitter scraper
npx skills add https://github.com/kohoj/skills --skill x-cdp-scraper

# Xiaohongshu to Markdown
npx skills add https://github.com/kohoj/skills --skill xhs-to-markdown
```

## Prerequisites

- A Chromium-based browser (Chrome, Edge, Brave, Arc)
- Python 3.8+
- `pip install playwright httpx && playwright install chromium`
- **xhs-to-markdown** additionally requires macOS (for Vision Framework OCR)

## License

MIT
