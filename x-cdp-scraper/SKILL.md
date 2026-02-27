---
name: x-cdp-scraper
description: "X/Twitter CDP Tweet Scraper — Bulk-fetch a user's tweets via browser CDP protocol. Use when a user needs to fully collect all tweets from a Twitter/X account. Covers: scraping all tweets for a given year, exporting a Twitter timeline, batch-fetching tweet data for analysis. Works with any Chromium-based browser (Chrome, Edge, Brave, Arc, etc.) — requires the user to be logged in to Twitter in the browser."
---

# X/Twitter CDP Tweet Scraper v2

Extracts authentication from a Chromium browser via CDP, then calls the Twitter GraphQL API directly with httpx for high-speed bulk tweet collection. Outputs JSON + Markdown.

## Quick Start

```bash
# By date range (recommended)
python3 <skill-path>/scripts/cdp_tweet_fetcher.py <username> --since 2026-02 [--until 2026-02-28] [--output-dir DIR]

# By year (shorthand)
python3 <skill-path>/scripts/cdp_tweet_fetcher.py <username> --year 2026 [--output-dir DIR]

# No date specified -> defaults to current year to date
python3 <skill-path>/scripts/cdp_tweet_fetcher.py <username> [--output-dir DIR]
```

**Arguments:**
- `username` (required): Twitter username (without @)
- `--since`: Start date (inclusive). Accepts `YYYY-MM-DD`, `YYYY-MM`, `YYYY`
- `--until`: End date (inclusive), defaults to today
- `--year`: Target year (shorthand for `--since YYYY-01-01`)
- `--output-dir`: Output directory, defaults to current working directory
- `--page-delay`: Seconds between API pages, default 1.0
- `--max-pages`: Maximum pages to fetch, default 200
- `--cdp-port`: CDP debugging port, default 9222

**Output files:**
- `{username}_tweets_{YYYYMMDD}_{YYYYMMDD}.json` — Full structured data
- `{username}_tweets_{YYYYMMDD}_{YYYYMMDD}.md` — Human-readable Markdown report

## Prerequisites

1. **Chromium-based browser** (Chrome / Edge / Brave / Arc / Chromium) installed and logged in to Twitter/X
2. **Python dependencies**: `pip install playwright httpx && playwright install chromium`
3. Browser must be launched with CDP enabled — the script auto-detects your OS and shows the correct launch command

**Launch browser with CDP (pick your browser):**

macOS:
```bash
# Chrome
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
# Edge
/Applications/Microsoft\ Edge.app/Contents/MacOS/Microsoft\ Edge --remote-debugging-port=9222
# Brave
/Applications/Brave\ Browser.app/Contents/MacOS/Brave\ Browser --remote-debugging-port=9222
# Arc
/Applications/Arc.app/Contents/MacOS/Arc --remote-debugging-port=9222
```

Linux:
```bash
google-chrome --remote-debugging-port=9222
# or: chromium-browser / microsoft-edge / brave-browser
```

Windows (PowerShell):
```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
# or: msedge.exe / brave.exe in their respective paths
```

## Architecture — Why It's Fast

v2 minimizes browser interaction: authentication is extracted once (~5 s), then all API calls go through httpx directly.

| Change | Effect |
|--------|--------|
| Browser only used for cookie + query ID extraction (one-time) | Init drops from ~18 s to ~5 s |
| httpx direct HTTP requests (no CDP round-trips) | Each API call 3-5x faster |
| Single endpoint: UserTweetsAndReplies (superset) | Half the pagination |
| count=40 (was 20) | Half the pagination again |
| page-delay 1.0 s (was 2.5 s) | 60% less wait per page |

## Execution Flow

1. **Connect to browser**: CDP connection, extract cookies and CSRF token
2. **Discover API**: Parse JS bundles for GraphQL query IDs (no page navigation)
3. **HTTP client**: Create httpx client with extracted auth
4. **Resolve user ID**: Via UserByScreenName API
5. **Bulk fetch**: UserTweetsAndReplies endpoint, 40 tweets/page, direct HTTP
6. **Output**: JSON + Markdown files

## Output Schema

Each tweet contains:

```json
{
  "tweet_id": "123456789",
  "text": "Full tweet text...",
  "datetime": "2026-01-15T10:30:00+00:00",
  "url": "https://x.com/user/status/123456789",
  "author": "username",
  "is_reply": false,
  "reply_to": null,
  "reply_to_tweet_id": null,
  "is_retweet": false,
  "retweet_of": null,
  "is_quote": false,
  "quoted_tweet_url": null,
  "likes": 100,
  "retweets": 20,
  "replies": 5,
  "bookmarks": 30,
  "views": 10000,
  "media": ["https://pbs.twimg.com/..."],
  "links": ["https://example.com/..."]
}
```
