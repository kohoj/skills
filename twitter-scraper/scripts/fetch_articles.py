#!/usr/bin/env python3
"""
Fetch Twitter/X Articles (long-form posts) via TweetResultByRestId API.

Reads a tweets JSON file (output of cdp_tweet_fetcher.py), finds article links,
fetches each article's Draft.js content_state, and converts to Markdown.

Usage:
  python3 fetch_articles.py <tweets_json> [--output-dir DIR] [--cdp-port 9222]
"""

import argparse
import asyncio
import json
import os
import re
import sys
import time

CDP_PORT = 9222
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

DEFAULT_FEATURES = {
    "creator_subscriptions_tweet_preview_api_enabled": True,
    "premium_content_api_read_enabled": False,
    "communities_web_enable_tweet_community_results_fetch": True,
    "c9s_tweet_anatomy_moderator_badge_enabled": True,
    "responsive_web_grok_analyze_button_fetch_trends_enabled": False,
    "responsive_web_grok_analyze_post_followups_enabled": True,
    "responsive_web_jetfuel_frame": True,
    "responsive_web_grok_share_attachment_enabled": True,
    "responsive_web_grok_annotations_enabled": True,
    "articles_preview_enabled": True,
    "responsive_web_edit_tweet_api_enabled": True,
    "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
    "view_counts_everywhere_api_enabled": True,
    "longform_notetweets_consumption_enabled": True,
    "responsive_web_twitter_article_tweet_consumption_enabled": True,
    "tweet_awards_web_tipping_enabled": False,
    "responsive_web_grok_show_grok_translated_post": True,
    "responsive_web_grok_analysis_button_from_backend": True,
    "post_ctas_fetch_enabled": True,
    "freedom_of_speech_not_reach_fetch_enabled": True,
    "standardized_nudges_misinfo": True,
    "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
    "longform_notetweets_rich_text_read_enabled": True,
    "longform_notetweets_inline_media_enabled": True,
    "profile_label_improvements_pcf_label_in_post_enabled": True,
    "responsive_web_profile_redirect_enabled": False,
    "rweb_tipjar_consumption_enabled": False,
    "verified_phone_label_enabled": False,
    "responsive_web_grok_image_annotation_enabled": True,
    "responsive_web_grok_imagine_annotation_enabled": True,
    "responsive_web_grok_community_note_auto_translation_is_enabled": False,
    "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
    "responsive_web_graphql_timeline_navigation_enabled": True,
    "responsive_web_enhance_cards_enabled": False,
}


def log(msg, level="INFO"):
    ts = time.strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}", flush=True)


def walk_find(obj, predicate):
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


def extract_article_info(tweets_json):
    with open(tweets_json) as f:
        data = json.load(f)
    tweets = data.get("tweets", [])
    username = data.get("username", "")
    articles = []
    seen = set()
    for t in tweets:
        if t.get("is_retweet"):
            continue
        text = t.get("text", "")
        links = t.get("links", [])
        all_text = text + " " + " ".join(links)
        urls = re.findall(r"https?://x\.com/i/article/(\d+)", all_text)
        for aid in urls:
            if aid not in seen:
                seen.add(aid)
                articles.append({
                    "article_id": aid,
                    "tweet_id": t.get("tweet_id", ""),
                    "date": t["datetime"][:10] if t.get("datetime") else "",
                    "url": f"https://x.com/i/article/{aid}",
                    "tweet_url": t.get("url", ""),
                    "author": t.get("author", username),
                })
    return articles


def content_state_to_markdown(content_state, media_entities=None):
    """Convert Draft.js content_state to Markdown."""
    blocks = content_state.get("blocks", [])
    raw_entity_map = content_state.get("entityMap", {})

    # entityMap can be a dict or a list — normalize to dict keyed by string index
    if isinstance(raw_entity_map, list):
        entity_map = {str(i): v for i, v in enumerate(raw_entity_map) if isinstance(v, dict)}
    elif isinstance(raw_entity_map, dict):
        entity_map = raw_entity_map
    else:
        entity_map = {}

    # Build media lookup from media_entities
    media_lookup = {}
    if media_entities:
        for me in media_entities:
            mid = me.get("media_id", "")
            info = me.get("media_info", {})
            img_url = info.get("original_img_url", "")
            if mid and img_url:
                media_lookup[mid] = img_url

    md_parts = []
    prev_type = None
    list_counter = 0

    for block in blocks:
        btype = block.get("type", "unstyled")
        text = block.get("text", "").strip()
        entity_ranges = block.get("entityRanges", [])
        inline_styles = block.get("inlineStyleRanges", [])

        # Apply inline styles
        if text and inline_styles:
            sorted_styles = sorted(inline_styles, key=lambda s: s["offset"], reverse=True)
            text_chars = list(text)
            for style in sorted_styles:
                start = style["offset"]
                end = start + style["length"]
                style_type = style.get("style", "")
                if start < len(text_chars) and end <= len(text_chars):
                    segment = "".join(text_chars[start:end])
                    if style_type == "Bold":
                        styled = f"**{segment}**"
                    elif style_type == "Italic":
                        styled = f"*{segment}*"
                    elif style_type == "Strikethrough":
                        styled = f"~~{segment}~~"
                    else:
                        styled = segment
                    text_chars[start:end] = list(styled)
            text = "".join(text_chars)

        # Apply entity links
        if entity_ranges and text:
            for er in sorted(entity_ranges, key=lambda e: e.get("offset", 0), reverse=True):
                entity_key = str(er.get("key", ""))
                entity = entity_map.get(entity_key, {})
                etype = entity.get("type", "")
                edata = entity.get("data", {})

                if etype == "LINK":
                    url = edata.get("url", "")
                    start = er["offset"]
                    end = start + er["length"]
                    link_text = text[start:end]
                    if url and link_text.strip():
                        text = text[:start] + f"[{link_text}]({url})" + text[end:]

        # Format by block type
        if btype == "header-one":
            md_parts.append(f"# {text}")
        elif btype == "header-two":
            md_parts.append(f"## {text}")
        elif btype == "header-three":
            md_parts.append(f"### {text}")
        elif btype == "unordered-list-item":
            md_parts.append(f"- {text}")
        elif btype == "ordered-list-item":
            if prev_type != "ordered-list-item":
                list_counter = 0
            list_counter += 1
            md_parts.append(f"{list_counter}. {text}")
        elif btype == "blockquote":
            md_parts.append(f"> {text}")
        elif btype == "atomic":
            for er in entity_ranges:
                entity_key = str(er.get("key", ""))
                entity = entity_map.get(entity_key, {})
                etype = entity.get("type", "")
                edata = entity.get("data", {})
                if etype == "IMAGE" or etype == "MEDIA":
                    mid = edata.get("mediaId", "")
                    img_url = media_lookup.get(mid, "")
                    if img_url:
                        md_parts.append(f"![image]({img_url})")
                    else:
                        md_parts.append(f"![image](media:{mid})")
            if not entity_ranges:
                block_data = block.get("data", {})
                mid = block_data.get("mediaId", "")
                if mid and mid in media_lookup:
                    md_parts.append(f"![image]({media_lookup[mid]})")
        elif btype == "code-block":
            md_parts.append(f"```\n{text}\n```")
        else:
            if text:
                md_parts.append(text)
            else:
                md_parts.append("")

        prev_type = btype

    return "\n\n".join(md_parts)


async def safe_dismiss(dialog):
    try:
        await dialog.dismiss()
    except Exception:
        pass


async def main():
    parser = argparse.ArgumentParser(
        description="Fetch Twitter/X Articles (long-form posts) from a tweets JSON file"
    )
    parser.add_argument("tweets_json", help="Path to tweets JSON file (output of cdp_tweet_fetcher.py)")
    parser.add_argument("--output-dir", default="./articles", help="Output directory for article Markdown files")
    parser.add_argument("--cdp-port", type=int, default=CDP_PORT, help=f"CDP debug port (default: {CDP_PORT})")
    args = parser.parse_args()

    import httpx
    from playwright.async_api import async_playwright

    articles = extract_article_info(args.tweets_json)
    if not articles:
        log("No articles found in the tweets JSON file")
        return

    log(f"Found {len(articles)} articles to fetch")
    os.makedirs(args.output_dir, exist_ok=True)

    # Phase 1: Extract auth from browser
    log("Extracting auth from browser...")
    pw = await async_playwright().__aenter__()
    try:
        browser = await pw.chromium.connect_over_cdp(f"http://127.0.0.1:{args.cdp_port}")
    except Exception:
        log(f"Cannot connect to CDP port {args.cdp_port}.", "ERROR")
        log("Start your browser with --remote-debugging-port=9222", "ERROR")
        sys.exit(1)

    ctx = browser.contexts[0]
    cookies_list = await ctx.cookies("https://x.com")
    auth_cookies = {c["name"]: c["value"] for c in cookies_list}
    csrf_token = auth_cookies.get("ct0", "")
    log(f"  Extracted {len(auth_cookies)} cookies")

    # Phase 2: Discover query IDs
    log("Discovering query IDs...")
    query_ids = {}
    page = await ctx.new_page()
    page.on("dialog", lambda d: asyncio.ensure_future(safe_dismiss(d)))

    def on_request(request):
        m = re.search(r"/graphql/([^/]+)/(\w+)", request.url)
        if m:
            query_ids[m.group(2)] = m.group(1)

    page.on("request", on_request)

    try:
        await page.goto(articles[0]["url"], wait_until="domcontentloaded", timeout=15000)
        await page.wait_for_timeout(5000)
    except Exception:
        pass
    await page.close()

    if "TweetResultByRestId" not in query_ids:
        log("TweetResultByRestId not found!", "ERROR")
        sys.exit(1)

    qid = query_ids["TweetResultByRestId"]
    log(f"  TweetResultByRestId: {qid}")

    # Phase 3: Setup HTTP client
    client = httpx.AsyncClient(
        headers={
            "authorization": f"Bearer {BEARER_TOKEN}",
            "x-csrf-token": csrf_token,
            "content-type": "application/json",
            "x-twitter-active-user": "yes",
            "x-twitter-auth-type": "OAuth2Session",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "referer": "https://x.com/",
            "origin": "https://x.com",
        },
        cookies={k: v for k, v in auth_cookies.items()},
        timeout=30.0,
        follow_redirects=True,
    )

    # Phase 4: Fetch all articles
    log("Fetching articles...")
    results = []

    for i, article in enumerate(articles, 1):
        tweet_id = article["tweet_id"]
        if not tweet_id:
            log(f"  [{i}/{len(articles)}] No tweet_id, skipping")
            continue

        variables = {
            "tweetId": tweet_id,
            "includePromotedContent": True,
            "withBirdwatchNotes": True,
            "withVoice": True,
            "withCommunity": True,
        }
        field_toggles = {
            "withArticleRichContentState": True,
            "withArticlePlainText": False,
        }
        url = f"https://x.com/i/api/graphql/{qid}/TweetResultByRestId"

        try:
            resp = await client.get(url, params={
                "variables": json.dumps(variables),
                "features": json.dumps(DEFAULT_FEATURES),
                "fieldToggles": json.dumps(field_toggles),
            })

            if resp.status_code != 200:
                resp = await client.post(url, json={
                    "variables": variables,
                    "features": DEFAULT_FEATURES,
                    "fieldToggles": field_toggles,
                })

            if resp.status_code == 200:
                data = resp.json()

                ars = walk_find(data, lambda o: "article_results" in o)
                if ars:
                    ar = ars[0]["article_results"]["result"]
                    title = ar.get("title", "")
                    content_state = ar.get("content_state", {})
                    media_entities = ar.get("media_entities", [])

                    if content_state and content_state.get("blocks"):
                        body = content_state_to_markdown(content_state, media_entities)

                        filename = f"{article['date']}_{article['article_id']}.md"
                        filepath = os.path.join(args.output_dir, filename)

                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(f"# {title}\n\n")
                            f.write(f"**Date:** {article['date']}\n")
                            f.write(f"**URL:** {article['url']}\n")
                            if article.get("tweet_url"):
                                f.write(f"**Tweet:** {article['tweet_url']}\n")
                            f.write(f"\n---\n\n")
                            f.write(body)

                        log(f"  [{i}/{len(articles)}] {title[:60]}  ({len(body)} chars)")
                        results.append(article["article_id"])
                    else:
                        log(f"  [{i}/{len(articles)}] No content_state blocks", "WARN")
                else:
                    log(f"  [{i}/{len(articles)}] No article_results found", "WARN")
            else:
                log(f"  [{i}/{len(articles)}] API error {resp.status_code}", "WARN")
        except Exception as e:
            log(f"  [{i}/{len(articles)}] Error: {e}", "ERROR")

        await asyncio.sleep(1.0)

    await client.aclose()
    await pw.__aexit__(None, None, None)
    log(f"\nDone! {len(results)}/{len(articles)} articles saved to {args.output_dir}")


if __name__ == "__main__":
    asyncio.run(main())
