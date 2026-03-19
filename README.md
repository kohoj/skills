# Claude Code Skills

A collection of [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills for web scraping, data extraction, and content conversion. Built on a shared CDP (Chrome DevTools Protocol) + httpx architecture for fast, authenticated access.

## Available Skills

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

## Prerequisites

- A Chromium-based browser (Chrome, Edge, Brave, Arc) with CDP enabled
- Python 3.8+
- `pip install playwright httpx && playwright install chromium`
- **xiaohongshu-to-markdown** additionally requires macOS (for Vision Framework OCR)

## License

MIT
