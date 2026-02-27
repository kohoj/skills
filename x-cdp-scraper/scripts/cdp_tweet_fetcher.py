#!/usr/bin/env python3
"""
X/Twitter CDP Tweet Fetcher v2 — Zero-Interference Edition

Architecture:
  - Browser auth extraction via CDP ctx.cookies() — NO tabs opened, invisible to user
  - Query ID discovery via JS bundle parsing — NO browser page navigation
  - All API calls via httpx (direct HTTP, no CDP round-trips)
  - Single endpoint: UserTweetsAndReplies (superset), 40 tweets/page
Usage:
  python3 cdp_tweet_fetcher.py <username> [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--output-dir DIR]
"""

import argparse
import asyncio
import json
import os
import re
import sys
import time
from datetime import datetime, date
from urllib.parse import quote, unquote

# ─── Dependency check ──────────────────────────────

try:
    import httpx
except ImportError:
    print("ERROR: httpx is required. Install it:")
    print("  pip install httpx")
    sys.exit(1)

# ─── Constants ─────────────────────────────────────

DEFAULT_CDP_PORT = 9222
TWITTER_EPOCH_MS = 1288834974657  # Twitter Snowflake epoch
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
DEFAULT_PAGE_DELAY = 1.0       # seconds between API pages
DEFAULT_MAX_PAGES = 200
RATE_LIMIT_PAUSE = 60
MAX_RETRIES = 3
SAVE_INTERVAL = 20             # save progress every N new tweets
TWEETS_PER_PAGE = 40           # up from 20

# ─── Cross-platform browser launch commands ────────

_MACOS_BROWSERS = {
    "Arc": "/Applications/Arc.app/Contents/MacOS/Arc --remote-debugging-port={port}",
    "Google Chrome": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome --remote-debugging-port={port}",
    "Chromium": "/Applications/Chromium.app/Contents/MacOS/Chromium --remote-debugging-port={port}",
    "Microsoft Edge": "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge --remote-debugging-port={port}",
    "Brave Browser": "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser --remote-debugging-port={port}",
}

_LINUX_BROWSERS = {
    "Google Chrome": "google-chrome --remote-debugging-port={port}",
    "Google Chrome (path)": "/usr/bin/google-chrome --remote-debugging-port={port}",
    "Chromium": "chromium-browser --remote-debugging-port={port}",
    "Chromium (path)": "/usr/bin/chromium-browser --remote-debugging-port={port}",
    "Microsoft Edge": "microsoft-edge --remote-debugging-port={port}",
    "Microsoft Edge (path)": "/usr/bin/microsoft-edge --remote-debugging-port={port}",
    "Brave Browser": "brave-browser --remote-debugging-port={port}",
    "Brave Browser (path)": "/usr/bin/brave-browser --remote-debugging-port={port}",
}

_WINDOWS_BROWSERS = {
    "Google Chrome": r'"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port={port}',
    "Google Chrome (x86)": r'"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port={port}',
    "Microsoft Edge": r'"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port={port}',
    "Brave Browser": r'"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" --remote-debugging-port={port}',
}


def _get_browser_launch_commands():
    """Return browser launch commands for the current OS."""
    if sys.platform == "darwin":
        return _MACOS_BROWSERS
    elif sys.platform == "win32":
        return _WINDOWS_BROWSERS
    else:  # linux and others
        return _LINUX_BROWSERS


BROWSER_LAUNCH_COMMANDS = _get_browser_launch_commands()

ENDPOINTS = {"UserTweets", "UserTweetsAndReplies", "TweetResultByRestId", "UserByScreenName"}

# Default GraphQL features — Twitter is lenient with these; they change slowly.
# If API calls start failing, update this dict.
DEFAULT_FEATURES = {
    "rweb_tipjar_consumption_enabled": True,
    "responsive_web_graphql_exclude_directive_enabled": True,
    "verified_phone_label_enabled": False,
    "creator_subscriptions_tweet_preview_api_enabled": True,
    "responsive_web_graphql_timeline_navigation_enabled": True,
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
    "communities_web_enable_tweet_community_results_fetch": True,
    "c9s_tweet_anatomy_moderator_badge_enabled": True,
    "articles_preview_enabled": True,
    "responsive_web_edit_tweet_api_enabled": True,
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
    "view_counts_everywhere_api_enabled": True,
    "longform_notetweets_consumption_enabled": True,
    "responsive_web_twitter_article_tweet_consumption_enabled": True,
    "tweet_awards_web_tipping_enabled": False,
    "creator_subscriptions_quote_tweet_preview_enabled": False,
    "freedom_of_speech_not_reach_fetch_enabled": True,
    "standardized_nudges_misinfo": True,
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
    "rweb_video_timestamps_enabled": True,
    "longform_notetweets_rich_text_read_enabled": True,
    "longform_notetweets_inline_media_enabled": True,
    "responsive_web_enhance_cards_enabled": False,
    "tweetypie_unmention_optimization_enabled": True,
    "responsive_web_text_conversations_enabled": False,
    "interactive_text_enabled": True,
    "responsive_web_media_download_video_enabled": False,
}

DEFAULT_FIELD_TOGGLES = {
    "withArticlePlainText": False,
}


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}", flush=True)


# ─── Utility Functions ─────────────────────────────

def snowflake_to_datetime(tweet_id: str) -> datetime:
    """Extract datetime from a Twitter Snowflake ID."""
    ts_ms = (int(tweet_id) >> 22) + TWITTER_EPOCH_MS
    return datetime.utcfromtimestamp(ts_ms / 1000)


def tweet_id_in_range(tweet_id: str, since_date, until_date) -> bool:
    """Check if a tweet ID falls within the given date range."""
    try:
        dt = snowflake_to_datetime(tweet_id)
        return since_date <= dt.date() <= until_date
    except (ValueError, OverflowError):
        return True


def parse_flexible_date(date_str: str) -> date:
    """Parse flexible date formats: YYYY-MM-DD, YYYY-MM, YYYY."""
    date_str = date_str.strip()
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    if re.match(r'^\d{4}-\d{2}$', date_str):
        return datetime.strptime(date_str + "-01", "%Y-%m-%d").date()
    if re.match(r'^\d{4}$', date_str):
        return date(int(date_str), 1, 1)
    raise ValueError(f"Cannot parse date: {date_str} (expected YYYY-MM-DD, YYYY-MM, or YYYY)")


def walk_find(obj, predicate):
    """Recursively walk a JSON object and collect items matching predicate."""
    results = []

    def _walk(o):
        if isinstance(o, dict):
            if predicate(o):
                results.append(o)
            for v in o.values():
                _walk(v)
        elif isinstance(o, list):
            for item in o:
                _walk(item)

    _walk(obj)
    return results


def find_cursor_bottom(obj):
    """Find the 'Bottom' cursor for pagination."""
    cursors = walk_find(obj, lambda o: o.get("cursorType") == "Bottom" and "value" in o)
    return cursors[0]["value"] if cursors else None


def extract_tweet_data(tweet_obj, target_username=None):
    """Extract structured tweet data from a GraphQL tweet object."""
    try:
        result = tweet_obj
        if result.get("__typename") == "TweetWithVisibilityResults":
            result = result.get("tweet", {})

        legacy = result.get("legacy", {})
        if not legacy:
            return None

        rest_id = result.get("rest_id", legacy.get("id_str", ""))
        if not rest_id:
            return None

        # User info
        core = result.get("core", {})
        user_results = core.get("user_results", {}).get("result", {})
        user_legacy = user_results.get("legacy", {})
        user_core = user_results.get("core", {})
        screen_name = user_legacy.get("screen_name") or user_core.get("screen_name") or ""

        # Full text: prioritize note_tweet for long tweets
        full_text = legacy.get("full_text", "")
        note_tweet = result.get("note_tweet", {})
        note_results = note_tweet.get("note_tweet_results", {})
        note_result = note_results.get("result", {})
        if note_result.get("text"):
            full_text = note_result["text"]

        # Expand t.co short links
        for u in legacy.get("entities", {}).get("urls", []):
            if u.get("url") and u.get("expanded_url"):
                full_text = full_text.replace(u["url"], u["expanded_url"])
        for entity_block in note_result.get("entity_set", {}).get("urls", []):
            if entity_block.get("url") and entity_block.get("expanded_url"):
                full_text = full_text.replace(entity_block["url"], entity_block["expanded_url"])

        # Remove trailing media t.co links
        full_text = re.sub(r'\s*https://t\.co/\w+$', '', full_text)

        # Datetime
        created_at = legacy.get("created_at", "")
        dt_str = ""
        if created_at:
            try:
                dt = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
                dt_str = dt.isoformat()
            except ValueError:
                dt_str = created_at

        # Reply info
        is_reply = bool(legacy.get("in_reply_to_screen_name"))
        reply_to = legacy.get("in_reply_to_screen_name", None)
        reply_to_tweet_id = legacy.get("in_reply_to_status_id_str", None)

        # Retweet info
        retweeted_status = legacy.get("retweeted_status_result", {}).get("result", {})
        is_retweet = bool(retweeted_status)
        retweet_of = None
        if is_retweet:
            rt_user = retweeted_status.get("core", {}).get("user_results", {}).get("result", {})
            retweet_of = rt_user.get("legacy", {}).get("screen_name") or rt_user.get("core", {}).get("screen_name")

        # Quote tweet info
        quoted_status = result.get("quoted_status_result", {}).get("result", {})
        is_quote = bool(quoted_status)
        quoted_tweet_url = None
        if is_quote:
            qt_legacy = quoted_status.get("legacy", {})
            qt_user = quoted_status.get("core", {}).get("user_results", {}).get("result", {})
            qt_screen_name = qt_user.get("legacy", {}).get("screen_name", "")
            qt_id = quoted_status.get("rest_id", qt_legacy.get("id_str", ""))
            if qt_screen_name and qt_id:
                quoted_tweet_url = f"https://x.com/{qt_screen_name}/status/{qt_id}"

        # Engagement metrics
        likes = legacy.get("favorite_count", 0)
        retweets_count = legacy.get("retweet_count", 0)
        replies_count = legacy.get("reply_count", 0)
        bookmarks = legacy.get("bookmark_count", 0)
        views_data = result.get("views", {})
        views = int(views_data.get("count", 0)) if views_data.get("count") else 0

        # Media
        media_list = legacy.get("extended_entities", {}).get("media", [])
        media_urls = []
        for m in media_list:
            if m.get("type") == "video" or m.get("type") == "animated_gif":
                variants = m.get("video_info", {}).get("variants", [])
                mp4_variants = [v for v in variants if v.get("content_type") == "video/mp4"]
                if mp4_variants:
                    best = max(mp4_variants, key=lambda v: v.get("bitrate", 0))
                    media_urls.append(best["url"])
                elif variants:
                    media_urls.append(variants[0].get("url", ""))
            else:
                media_urls.append(m.get("media_url_https", ""))

        # External links
        links = []
        for u in legacy.get("entities", {}).get("urls", []):
            expanded = u.get("expanded_url", u.get("url", ""))
            if expanded and "t.co" not in expanded:
                links.append(expanded)

        return {
            "tweet_id": rest_id,
            "text": full_text.strip(),
            "datetime": dt_str,
            "url": f"https://x.com/{screen_name}/status/{rest_id}",
            "author": screen_name,
            "is_reply": is_reply,
            "reply_to": f"@{reply_to}" if reply_to else None,
            "reply_to_tweet_id": reply_to_tweet_id,
            "is_retweet": is_retweet,
            "retweet_of": f"@{retweet_of}" if retweet_of else None,
            "is_quote": is_quote,
            "quoted_tweet_url": quoted_tweet_url,
            "likes": likes,
            "retweets": retweets_count,
            "replies": replies_count,
            "bookmarks": bookmarks,
            "views": views,
            "media": media_urls,
            "links": links,
        }
    except Exception:
        return None


def filter_by_date_range(tweets, since, until):
    """Filter tweets by date range using datetime field."""
    filtered = []
    for t in tweets:
        dt_str = t.get("datetime", "")
        if not dt_str:
            filtered.append(t)
            continue
        try:
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            if since <= dt.date() <= until:
                filtered.append(t)
        except (ValueError, TypeError):
            filtered.append(t)
    return filtered


def tweet_is_before_date(tweet, target_date):
    """Check if a tweet is before the target date."""
    dt_str = tweet.get("datetime", "")
    if not dt_str:
        return False
    try:
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.date() < target_date
    except (ValueError, TypeError):
        return False


def deduplicate(tweets):
    """Deduplicate tweets by tweet_id."""
    seen = set()
    result = []
    for t in tweets:
        tid = t.get("tweet_id")
        if tid and tid not in seen:
            seen.add(tid)
            result.append(t)
    return result


def generate_markdown(tweets, username, date_label):
    """Generate a readable Markdown report."""
    lines = [
        f"# @{username} Tweets ({date_label})",
        f"",
        f"Total: {len(tweets)} tweets",
        f"",
        f"---",
        f"",
    ]

    originals = [t for t in tweets if not t.get("is_reply") and not t.get("is_retweet")]
    replies = [t for t in tweets if t.get("is_reply")]
    retweets = [t for t in tweets if t.get("is_retweet")]
    quotes = [t for t in tweets if t.get("is_quote")]
    lines.append(f"**Stats:** {len(originals)} original, {len(replies)} replies, {len(retweets)} retweets, {len(quotes)} quotes")
    lines.append(f"")
    lines.append(f"---")
    lines.append(f"")

    for t in tweets:
        type_tag = ""
        if t.get("is_retweet"):
            type_tag = f" RT {t.get('retweet_of', '')}"
        elif t.get("is_reply"):
            type_tag = f" Reply to {t.get('reply_to', '')}"
        elif t.get("is_quote"):
            type_tag = " Quote"

        lines.append(f"### {t.get('datetime', 'Unknown date')}{type_tag}")
        lines.append(f"")
        lines.append(t.get("text", ""))
        lines.append(f"")

        lines.append(f"Likes: {t.get('likes', 0)} | RT: {t.get('retweets', 0)} | Replies: {t.get('replies', 0)} | Bookmarks: {t.get('bookmarks', 0)} | Views: {t.get('views', 0)}")

        if t.get("media"):
            lines.append(f"")
            for url in t["media"]:
                lines.append(f"![media]({url})")

        if t.get("links"):
            lines.append(f"")
            for link in t["links"]:
                lines.append(f"Link: {link}")

        if t.get("quoted_tweet_url"):
            lines.append(f"")
            lines.append(f"Quoted: {t['quoted_tweet_url']}")

        lines.append(f"")
        lines.append(f"[Original]({t.get('url', '')})")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")

    return "\n".join(lines)


# ─── Core Fetcher ──────────────────────────────────

class CDPTweetFetcher:
    def __init__(self, username, year=None, since=None, until=None,
                 output_dir=".", page_delay=DEFAULT_PAGE_DELAY,
                 max_pages=DEFAULT_MAX_PAGES, cdp_port=DEFAULT_CDP_PORT,
):
        self.username = username
        self.output_dir = output_dir
        self.page_delay = page_delay
        self.max_pages = max_pages
        self.cdp_port = cdp_port

        # Date range
        if since:
            self.since = parse_flexible_date(since) if isinstance(since, str) else since
        elif year:
            self.since = date(year, 1, 1)
        else:
            self.since = date(datetime.now().year, 1, 1)

        if until:
            self.until = parse_flexible_date(until) if isinstance(until, str) else until
        else:
            self.until = date.today()

        self.year = year or self.since.year
        self.date_label = f"{self.since.isoformat()} ~ {self.until.isoformat()}"

        # Auth
        self.csrf_token = ""
        self.auth_cookies = {}
        self.http_client = None

        # API discovery
        self.query_ids = {}
        self.query_params = {}  # endpoint -> {features, fieldToggles}
        self.user_id = None

        # Data
        self.all_tweets = {}
        self.progress_file = os.path.join(output_dir, f"{username}_progress.json")

        # Playwright (kept alive for fallbacks)
        self._playwright = None
        self._browser = None

        log(f"Target: @{username}, {self.date_label}")

    async def run(self):
        """Main execution flow."""
        t_start = time.time()
        try:
            # Phase 1: Extract auth from browser — invisible, no tabs
            t0 = time.time()
            await self._extract_auth_from_browser()
            log(f"  Auth done ({time.time() - t0:.1f}s)")

            # Phase 2: Setup HTTP client
            self._setup_http_client()

            # Phase 3: Discover query IDs from JS bundles — no browser pages
            t0 = time.time()
            js_ok = await self._discover_query_ids_from_js()
            if not js_ok:
                log("  JS bundle discovery failed, falling back to browser page...", "WARN")
                await self._discover_query_ids_from_browser()
            log(f"  Query ID discovery done ({time.time() - t0:.1f}s)")

            # Phase 4: Resolve user ID
            await self._resolve_user_id()

            # Phase 5: Batch fetch
            t0 = time.time()
            await self._fetch_all_tweets()
            log(f"  Fetch done ({time.time() - t0:.1f}s)")

            # Phase 6: Output
            self._save_output()

            elapsed = time.time() - t_start
            in_range = filter_by_date_range(list(self.all_tweets.values()), self.since, self.until)
            log(f"Done! {len(in_range)} tweets in {self.date_label} ({elapsed:.1f}s)")
        except Exception as e:
            log(f"Error: {e}", "ERROR")
            self._save_progress()
            raise
        finally:
            await self._cleanup()

    # ── Phase 1: Invisible auth extraction ──

    async def _extract_auth_from_browser(self):
        """Extract cookies via CDP ctx.cookies(). NO pages opened — completely invisible."""
        from playwright.async_api import async_playwright

        log("Extracting auth from browser (invisible — no tabs opened)...")
        self._playwright = await async_playwright().__aenter__()

        try:
            self._browser = await self._playwright.chromium.connect_over_cdp(
                f"http://127.0.0.1:{self.cdp_port}"
            )
        except Exception:
            log(f"Cannot connect to CDP port {self.cdp_port}.", "ERROR")
            log("Start your browser with CDP enabled:", "ERROR")
            for name, cmd in BROWSER_LAUNCH_COMMANDS.items():
                # On macOS, check if the binary exists; on other platforms just show all
                if sys.platform == "darwin":
                    bin_path = cmd.split(" --")[0].strip('"')
                    if not os.path.exists(bin_path):
                        continue
                log(f"  {name}: {cmd.format(port=self.cdp_port)}", "ERROR")
            raise SystemExit(1)

        ctx = self._browser.contexts[0]

        # Read cookies directly from cookie jar — no page needed
        cookies_list = await ctx.cookies("https://x.com")
        self.auth_cookies = {c["name"]: c["value"] for c in cookies_list}
        self.csrf_token = self.auth_cookies.get("ct0", "")

        if not self.csrf_token or "auth_token" not in self.auth_cookies:
            log("Not logged in to Twitter. Please log in at x.com in your browser first.", "ERROR")
            raise SystemExit(1)

        log(f"  Extracted {len(self.auth_cookies)} cookies (invisible)")

    # ── Phase 2: HTTP client ──

    def _setup_http_client(self):
        """Create httpx client with extracted browser auth."""
        self.http_client = httpx.AsyncClient(
            headers={
                "authorization": f"Bearer {BEARER_TOKEN}",
                "x-csrf-token": self.csrf_token,
                "content-type": "application/json",
                "x-twitter-active-user": "yes",
                "x-twitter-auth-type": "OAuth2Session",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "referer": "https://x.com/",
                "origin": "https://x.com",
            },
            cookies={k: v for k, v in self.auth_cookies.items()},
            timeout=30.0,
            follow_redirects=True,
        )
        log("HTTP client ready")

    # ── Phase 3: Query ID discovery from JS bundles ──

    async def _discover_query_ids_from_js(self):
        """Discover GraphQL query IDs by parsing Twitter's JS bundles. No browser interaction."""
        log("Discovering query IDs from JS bundles...")

        # Fetch x.com main page HTML
        try:
            resp = await self.http_client.get("https://x.com")
        except Exception as e:
            log(f"  Failed to fetch x.com: {e}", "WARN")
            return False

        if resp.status_code != 200:
            log(f"  x.com returned {resp.status_code}", "WARN")
            return False

        html = resp.text

        # Find JS bundle URLs from script tags
        # Twitter uses abs.twimg.com for static assets
        script_urls = re.findall(
            r'src=["\']([^"\']*(?:abs\.twimg\.com|twimg\.com)[^"\']*\.js)["\']',
            html
        )
        if not script_urls:
            # Broader fallback: any script with client-web in path
            script_urls = re.findall(r'src=["\']([^"\']+client-web[^"\']+\.js)["\']', html)
        if not script_urls:
            # Even broader: all script srcs
            script_urls = re.findall(r'<script[^>]+src=["\']([^"\']+\.js)["\']', html)

        if not script_urls:
            log("  No JS bundle URLs found in HTML", "WARN")
            return False

        log(f"  Found {len(script_urls)} JS bundles, scanning for query IDs...")

        # Fetch bundles in parallel and extract query IDs
        target_ops = {"UserTweets", "UserTweetsAndReplies", "TweetResultByRestId", "UserByScreenName"}
        found = {}

        async def fetch_and_search(url):
            # Ensure absolute URL
            if url.startswith("//"):
                url = "https:" + url
            elif url.startswith("/"):
                url = "https://x.com" + url
            try:
                r = await self.http_client.get(url, timeout=15.0)
                if r.status_code != 200:
                    return
                text = r.text
                # Pattern: queryId:"xxx",operationName:"yyy"
                # Handle both single and double quotes, with optional spaces
                matches = re.findall(
                    r'queryId\s*:\s*["\']([^"\']+)["\']\s*,\s*operationName\s*:\s*["\']([^"\']+)["\']',
                    text
                )
                for qid, op_name in matches:
                    if op_name in target_ops and op_name not in found:
                        found[op_name] = qid
            except Exception:
                pass

        # Fetch all bundles concurrently
        tasks = [fetch_and_search(url) for url in script_urls]
        await asyncio.gather(*tasks)

        if not found:
            log("  No query IDs found in JS bundles", "WARN")
            return False

        self.query_ids = found
        # Use default features since we can't extract them from bundles reliably
        for ep in found:
            self.query_params[ep] = {
                "features": DEFAULT_FEATURES.copy(),
                "fieldToggles": DEFAULT_FIELD_TOGGLES.copy(),
            }

        display = ", ".join(f"{k}={v[:10]}..." for k, v in found.items())
        log(f"  Discovered from JS: {display}")

        if not any(k in found for k in ["UserTweets", "UserTweetsAndReplies"]):
            log("  Missing timeline endpoint, will try browser fallback", "WARN")
            return False

        return True

    async def _discover_query_ids_from_browser(self):
        """Fallback: discover query IDs by opening a browser page and intercepting requests.
        NOTE: This WILL open a visible tab in the user's browser."""
        log("  Opening browser tab for query ID discovery (fallback)...")

        ctx = self._browser.contexts[0]
        page = await ctx.new_page()
        captured = {}
        captured_params = {}

        def _extract_from_url(url):
            try:
                after = url.split("/graphql/")[1]
                parts = after.split("?")[0].split("/")
                return (parts[0], parts[1]) if len(parts) >= 2 else (None, None)
            except (IndexError, ValueError):
                return None, None

        def on_response(response):
            url = response.url
            if "/graphql/" not in url:
                return
            qid, ep = _extract_from_url(url)
            if not qid or ep not in ENDPOINTS:
                return
            captured[ep] = qid
            if "?" in url:
                for kv in url.split("?", 1)[1].split("&"):
                    if "=" in kv:
                        k, v = kv.split("=", 1)
                        if k in ("features", "fieldToggles"):
                            try:
                                captured_params.setdefault(ep, {})[k] = json.loads(unquote(v))
                            except (json.JSONDecodeError, TypeError):
                                pass

        def on_request(request):
            url = request.url
            if "/graphql/" not in url:
                return
            _, ep = _extract_from_url(url)
            if not ep or ep not in ENDPOINTS:
                return
            if request.method == "POST" and request.post_data:
                try:
                    data = json.loads(request.post_data)
                    for k in ("features", "fieldToggles"):
                        if k in data and isinstance(data[k], dict):
                            captured_params.setdefault(ep, {})[k] = data[k]
                except (json.JSONDecodeError, TypeError):
                    pass

        page.on("response", on_response)
        page.on("request", on_request)

        await page.goto(f"https://x.com/{self.username}/with_replies", wait_until="domcontentloaded")
        for _ in range(12):
            await asyncio.sleep(0.5)
            if "UserTweetsAndReplies" in captured and "UserByScreenName" in captured:
                break

        if "UserTweetsAndReplies" not in captured and "UserTweets" not in captured:
            await page.goto(f"https://x.com/{self.username}", wait_until="domcontentloaded")
            for _ in range(8):
                await asyncio.sleep(0.5)
                if "UserTweets" in captured:
                    break

        page.remove_listener("response", on_response)
        page.remove_listener("request", on_request)
        await page.close()

        # Merge with any existing query IDs (JS bundle results)
        self.query_ids.update(captured)
        for ep, params in captured_params.items():
            self.query_params.setdefault(ep, {}).update(params)

        found = ", ".join(f"{k}={v[:10]}..." for k, v in self.query_ids.items())
        log(f"  Query IDs (browser): {found}")

        if not any(k in self.query_ids for k in ["UserTweets", "UserTweetsAndReplies"]):
            log("No timeline query ID discovered", "ERROR")
            raise SystemExit(1)

    # ── API calls ──

    async def _api_call(self, qid, endpoint, variables, features, field_toggles=None):
        """Direct HTTP GET to Twitter GraphQL API."""
        params = {
            "variables": json.dumps(variables, ensure_ascii=False),
            "features": json.dumps(features, ensure_ascii=False),
        }
        if field_toggles:
            params["fieldToggles"] = json.dumps(field_toggles, ensure_ascii=False)

        url = f"https://x.com/i/api/graphql/{qid}/{endpoint}"
        resp = await self.http_client.get(url, params=params)

        if resp.status_code == 429:
            return {"__rate_limited": True, "status": 429}
        if resp.status_code >= 400:
            return {"__error": True, "status": resp.status_code, "text": resp.text[:200]}

        return resp.json()

    async def _api_call_post(self, qid, endpoint, variables, features, field_toggles=None):
        """Direct HTTP POST to Twitter GraphQL API — fallback for GET failures."""
        body = {"variables": variables, "features": features}
        if field_toggles:
            body["fieldToggles"] = field_toggles

        url = f"https://x.com/i/api/graphql/{qid}/{endpoint}"
        resp = await self.http_client.post(url, json=body)

        if resp.status_code == 429:
            return {"__rate_limited": True, "status": 429}
        if resp.status_code >= 400:
            return {"__error": True, "status": resp.status_code, "text": resp.text[:200]}

        return resp.json()

    # ── Resolve user ID ──

    async def _resolve_user_id(self):
        """Resolve numeric user ID via API."""
        log(f"Resolving @{self.username} user ID...")

        # Method 1: Via UserByScreenName API
        if "UserByScreenName" in self.query_ids:
            qid = self.query_ids["UserByScreenName"]
            variables = {"screen_name": self.username, "withSafetyModeUserFields": True}
            features = self._resolve_features("UserByScreenName")

            try:
                data = await self._api_call(qid, "UserByScreenName", variables, features)
                if data and not (isinstance(data, dict) and (data.get("__error") or data.get("__rate_limited"))):
                    users = walk_find(data, lambda o: o.get("__typename") == "User" and "rest_id" in o)
                    if users:
                        self.user_id = users[0]["rest_id"]
                        log(f"  User ID: {self.user_id}")
                        return
            except Exception as e:
                log(f"  API lookup failed: {e}", "WARN")

        # Method 2: Extract from browser page DOM (fallback)
        log("  Trying DOM extraction for user ID...")
        try:
            ctx = self._browser.contexts[0]
            page = await ctx.new_page()
            await page.goto(f"https://x.com/{self.username}", wait_until="domcontentloaded")
            await asyncio.sleep(2)

            uid = await page.evaluate("""() => {
                const scripts = document.querySelectorAll('script[type="application/json"]');
                for (const s of scripts) {
                    try {
                        const data = JSON.parse(s.textContent);
                        const str = JSON.stringify(data);
                        const match = str.match(/"rest_id":"(\\d+)"/);
                        if (match) return match[1];
                    } catch {}
                }
                return null;
            }""")
            await page.close()

            if uid:
                self.user_id = uid
                log(f"  User ID (from DOM): {uid}")
                return
        except Exception as e:
            log(f"  DOM extraction failed: {e}", "WARN")

        log("Cannot resolve user ID", "ERROR")
        raise SystemExit(1)

    # ── Batch fetch ──

    async def _fetch_all_tweets(self):
        """Fetch tweets from single best endpoint, 40/page, direct HTTP."""
        if not self.user_id:
            return

        self._load_progress()

        # Prefer UserTweetsAndReplies (superset), fallback to UserTweets
        endpoint = "UserTweetsAndReplies" if "UserTweetsAndReplies" in self.query_ids else "UserTweets"
        await self._paginate_endpoint(endpoint)

        log(f"  Total collected: {len(self.all_tweets)} tweets")

    def _resolve_features(self, endpoint):
        """Get features for an endpoint, with defaults as fallback."""
        features = self.query_params.get(endpoint, {}).get("features", {})
        if features:
            return features
        # Try borrowing from sibling timeline endpoint
        for sibling in ["UserTweetsAndReplies", "UserTweets", "UserByScreenName"]:
            if sibling != endpoint:
                f = self.query_params.get(sibling, {}).get("features", {})
                if f:
                    return f
        # Fall back to hardcoded defaults
        return DEFAULT_FEATURES.copy()

    async def _paginate_endpoint(self, endpoint):
        """Paginate through timeline endpoint with count=40."""
        qid = self.query_ids[endpoint]
        features = self._resolve_features(endpoint)
        field_toggles = self.query_params.get(endpoint, {}).get("fieldToggles", DEFAULT_FIELD_TOGGLES)

        log(f"  Paginating {endpoint} (count={TWEETS_PER_PAGE})...")
        cursor = None
        empty_streak = 0
        page_num = 0
        use_post = False

        while page_num < self.max_pages:
            page_num += 1
            variables = {
                "userId": self.user_id,
                "count": TWEETS_PER_PAGE,
                "includePromotedContent": True,
                "withCommunity": True,
                "withVoice": True,
                "withV2Timeline": True,
            }
            if cursor:
                variables["cursor"] = cursor

            # Request with retry
            data = None
            for attempt in range(MAX_RETRIES):
                try:
                    if use_post:
                        data = await self._api_call_post(qid, endpoint, variables, features, field_toggles)
                    else:
                        data = await self._api_call(qid, endpoint, variables, features, field_toggles)
                except Exception as e:
                    log(f"    Request error: {e}", "WARN")
                    await asyncio.sleep(3)
                    continue

                if isinstance(data, dict) and data.get("__rate_limited"):
                    log(f"    Rate limited, pausing {RATE_LIMIT_PAUSE}s ({attempt + 1}/{MAX_RETRIES})...", "WARN")
                    await asyncio.sleep(RATE_LIMIT_PAUSE)
                    continue

                if isinstance(data, dict) and data.get("__error"):
                    status = data.get("status")
                    log(f"    API error {status}: {data.get('text', '')[:100]}", "WARN")
                    if not use_post and status in (422, 404, 400):
                        log("    Switching to POST mode...", "INFO")
                        use_post = True
                        continue
                    await asyncio.sleep(5)
                    continue

                break

            if not data or (isinstance(data, dict) and (data.get("__rate_limited") or data.get("__error"))):
                log(f"    Page {page_num} failed after retries, stopping", "WARN")
                break

            # Extract tweets
            tweet_objs = walk_find(
                data,
                lambda o: o.get("__typename") in ("Tweet", "TweetWithVisibilityResults")
                and ("legacy" in o or "tweet" in o)
            )

            new_count = 0
            old_count = 0
            page_total = 0
            for obj in tweet_objs:
                tweet = extract_tweet_data(obj, self.username)
                if not tweet or not tweet.get("tweet_id"):
                    continue
                page_total += 1

                if tweet["tweet_id"] not in self.all_tweets:
                    self.all_tweets[tweet["tweet_id"]] = tweet
                    new_count += 1

                if tweet_is_before_date(tweet, self.since):
                    old_count += 1

            log(f"    p{page_num}: +{new_count} new, {old_count} old | total: {len(self.all_tweets)}")

            # Periodic progress save
            if new_count > 0 and len(self.all_tweets) % SAVE_INTERVAL < new_count:
                self._save_progress()

            # Stop: all tweets on page are before target date
            if page_total > 0 and old_count >= page_total:
                log(f"    All tweets before {self.since}, done")
                break

            # Stop: consecutive empty pages
            if new_count > 0:
                empty_streak = 0
            else:
                empty_streak += 1

            if empty_streak >= 3:
                log(f"    {empty_streak} consecutive empty pages, done")
                break

            # Next page
            next_cursor = find_cursor_bottom(data)
            if not next_cursor:
                log(f"    No more pages")
                break
            cursor = next_cursor

            await asyncio.sleep(self.page_delay)

    # ── Progress Management ──

    def _save_progress(self):
        """Save fetching progress."""
        try:
            with open(self.progress_file, "w", encoding="utf-8") as f:
                json.dump({
                    "username": self.username,
                    "year": self.year,
                    "total_collected": len(self.all_tweets),
                    "timestamp": datetime.now().isoformat(),
                    "tweets": self.all_tweets,
                }, f, ensure_ascii=False)
        except Exception as e:
            log(f"Failed to save progress: {e}", "WARN")

    def _load_progress(self):
        """Load previous fetching progress."""
        if not os.path.exists(self.progress_file):
            return
        try:
            with open(self.progress_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("username") == self.username and data.get("year") == self.year:
                tweets = data.get("tweets", {})
                if isinstance(tweets, dict) and len(tweets) > 0:
                    self.all_tweets.update(tweets)
                    log(f"  Restored progress: {len(tweets)} existing tweets")
        except Exception as e:
            log(f"Failed to load progress: {e}", "WARN")

    # ── Output ──

    def _save_output(self):
        """Generate final output files."""
        os.makedirs(self.output_dir, exist_ok=True)

        all_tweets_list = list(self.all_tweets.values())
        filtered_tweets = filter_by_date_range(all_tweets_list, self.since, self.until)
        filtered_tweets = deduplicate(filtered_tweets)
        filtered_tweets.sort(key=lambda t: t.get("datetime", ""), reverse=True)

        log(f"  Total collected: {len(all_tweets_list)} -> {self.date_label}: {len(filtered_tweets)} tweets")

        file_tag = f"{self.since.strftime('%Y%m%d')}_{self.until.strftime('%Y%m%d')}"
        json_path = os.path.join(self.output_dir, f"{self.username}_tweets_{file_tag}.json")
        md_path = os.path.join(self.output_dir, f"{self.username}_tweets_{file_tag}.md")

        if len(filtered_tweets) == 0 and os.path.exists(json_path):
            log("  Warning: 0 tweets collected, not overwriting existing file", "WARN")
            return

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "username": self.username,
                "since": self.since.isoformat(),
                "until": self.until.isoformat(),
                "count": len(filtered_tweets),
                "fetched_at": datetime.now().isoformat(),
                "tweets": filtered_tweets,
            }, f, ensure_ascii=False, indent=2)
        log(f"  Saved JSON: {json_path}")

        md_content = generate_markdown(filtered_tweets, self.username, self.date_label)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        log(f"  Saved Markdown: {md_path}")

        if os.path.exists(self.progress_file):
            os.remove(self.progress_file)

        originals = [t for t in filtered_tweets if not t.get("is_reply") and not t.get("is_retweet")]
        replies = [t for t in filtered_tweets if t.get("is_reply")]
        retweets = [t for t in filtered_tweets if t.get("is_retweet")]
        quotes = [t for t in filtered_tweets if t.get("is_quote")]
        print(f"\n{'=' * 50}")
        print(f"  @{self.username} Tweet Stats ({self.date_label})")
        print(f"{'=' * 50}")
        print(f"  Total: {len(filtered_tweets)}")
        print(f"  Original: {len(originals)}")
        print(f"  Replies: {len(replies)}")
        print(f"  Retweets: {len(retweets)}")
        print(f"  Quotes: {len(quotes)}")
        print(f"{'=' * 50}\n")

    # ── Cleanup ──

    async def _cleanup(self):
        """Clean up resources."""
        if self.http_client:
            try:
                await self.http_client.aclose()
                self.http_client = None
            except Exception:
                pass
        if self._playwright:
            try:
                await self._playwright.__aexit__(None, None, None)
                self._playwright = None
            except Exception:
                pass


# ─── CLI ───────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="X/Twitter CDP Tweet Fetcher v2 — Zero-Interference Edition",
        epilog="Date formats: YYYY-MM-DD, YYYY-MM, YYYY. Example: --since 2026-02 --until 2026-02-28"
    )
    parser.add_argument("username", help="Twitter username (without @)")
    parser.add_argument("--since", type=str, default=None, help="Start date (inclusive)")
    parser.add_argument("--until", type=str, default=None, help="End date (inclusive), defaults to today")
    parser.add_argument("--year", type=int, default=None, help="Target year (shorthand for --since YYYY-01-01)")
    parser.add_argument("--output-dir", default=".", help="Output directory (default: current dir)")
    parser.add_argument("--page-delay", type=float, default=DEFAULT_PAGE_DELAY, help=f"Delay between pages in seconds (default: {DEFAULT_PAGE_DELAY})")
    parser.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES, help=f"Max pages to fetch (default: {DEFAULT_MAX_PAGES})")
    parser.add_argument("--cdp-port", type=int, default=DEFAULT_CDP_PORT, help=f"CDP debug port (default: {DEFAULT_CDP_PORT})")

    args = parser.parse_args()

    fetcher = CDPTweetFetcher(
        username=args.username,
        year=args.year,
        since=args.since,
        until=args.until,
        output_dir=args.output_dir,
        page_delay=args.page_delay,
        max_pages=args.max_pages,
        cdp_port=args.cdp_port,
    )

    asyncio.run(fetcher.run())


if __name__ == "__main__":
    main()
