#!/usr/bin/env python3
"""
Xiaohongshu Article to Markdown — CDP + HTTP + macOS Vision OCR

Architecture:
  - Browser cookie extraction via CDP ctx.cookies() — invisible to user
  - httpx GET page HTML, extract __INITIAL_STATE__ JSON
  - Parse note data: title, desc, imageList, user info
  - Download high-res images via httpx
  - macOS Vision OCR via Swift helper
  - Compose and save Markdown

Usage:
  python3 xhs_to_markdown.py <url> [--output-dir DIR] [--cdp-port PORT]
"""

import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from urllib.parse import urlparse

# ─── Dependency check ──────────────────────────────

try:
    import httpx
except ImportError:
    print("ERROR: httpx is required. Install it:")
    print("  pip install httpx")
    sys.exit(1)

# ─── Constants ─────────────────────────────────────

DEFAULT_CDP_PORT = 9222
XHS_DOMAIN = "www.xiaohongshu.com"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

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
    "Chromium": "chromium-browser --remote-debugging-port={port}",
    "Microsoft Edge": "microsoft-edge --remote-debugging-port={port}",
    "Brave Browser": "brave-browser --remote-debugging-port={port}",
}

_WINDOWS_BROWSERS = {
    "Google Chrome": r'"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port={port}',
    "Microsoft Edge": r'"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port={port}',
    "Brave Browser": r'"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe" --remote-debugging-port={port}',
}


def _get_browser_launch_commands():
    if sys.platform == "darwin":
        return _MACOS_BROWSERS
    elif sys.platform == "win32":
        return _WINDOWS_BROWSERS
    else:
        return _LINUX_BROWSERS


BROWSER_LAUNCH_COMMANDS = _get_browser_launch_commands()


# ─── Utility Functions ─────────────────────────────

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] [{level}] {msg}", flush=True)


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


def extract_note_id(url):
    """Extract note ID from various Xiaohongshu URL formats."""
    # /explore/{noteId}
    m = re.search(r'/explore/([a-f0-9]+)', url)
    if m:
        return m.group(1)
    # /discovery/item/{noteId}
    m = re.search(r'/discovery/item/([a-f0-9]+)', url)
    if m:
        return m.group(1)
    # /item/{noteId}  (generic)
    m = re.search(r'/item/([a-f0-9]+)', url)
    if m:
        return m.group(1)
    # Fallback: last hex segment in path
    m = re.search(r'/([a-f0-9]{24})', url)
    if m:
        return m.group(1)
    return None


def sanitize_filename(name, max_len=80):
    """Make a string safe for use as a filename."""
    # Remove characters unsafe for filesystems
    name = re.sub(r'[\\/:*?"<>|\n\r\t]', '', name)
    # Collapse whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    if len(name) > max_len:
        name = name[:max_len].rstrip()
    return name or "untitled"


# ─── Core Class ────────────────────────────────────

class XhsToMarkdown:
    def __init__(self, url, output_dir=".", cdp_port=DEFAULT_CDP_PORT):
        self.url = url
        self.output_dir = output_dir
        self.cdp_port = cdp_port

        self.note_id = extract_note_id(url)
        if not self.note_id:
            log(f"Cannot extract note ID from URL: {url}", "ERROR")
            raise SystemExit(1)

        self.cookies = {}
        self.http_client = None
        self._playwright = None
        self._browser = None

        log(f"Target: {url} (note_id={self.note_id})")

    async def run(self):
        t_start = time.time()
        try:
            await self._extract_cookies()
            self._setup_http_client()
            page_data = await self._fetch_page_data()
            note = self._parse_note_data(page_data)
            image_paths = await self._download_images(note["images"])
            texts = self._ocr_images(image_paths)
            markdown = self._compose_markdown(note, texts)
            self._save_output(markdown, note)

            elapsed = time.time() - t_start
            log(f"Done! ({elapsed:.1f}s)")
        except SystemExit:
            raise
        except Exception as e:
            log(f"Error: {e}", "ERROR")
            raise
        finally:
            await self._cleanup()

    # ── CDP cookie extraction ──

    async def _extract_cookies(self):
        """Extract cookies via CDP. No tabs opened — invisible to user."""
        from playwright.async_api import async_playwright

        log("Extracting cookies from browser (invisible)...")
        self._playwright = await async_playwright().__aenter__()

        try:
            self._browser = await self._playwright.chromium.connect_over_cdp(
                f"http://127.0.0.1:{self.cdp_port}"
            )
        except Exception:
            log(f"Cannot connect to CDP port {self.cdp_port}.", "ERROR")
            log("Start your browser with CDP enabled:", "ERROR")
            for name, cmd in BROWSER_LAUNCH_COMMANDS.items():
                if sys.platform == "darwin":
                    bin_path = cmd.split(" --")[0].strip('"')
                    if not os.path.exists(bin_path):
                        continue
                log(f"  {name}: {cmd.format(port=self.cdp_port)}", "ERROR")
            raise SystemExit(1)

        ctx = self._browser.contexts[0]
        cookies_list = await ctx.cookies(f"https://{XHS_DOMAIN}")
        self.cookies = {c["name"]: c["value"] for c in cookies_list}

        if not self.cookies:
            log("No cookies found. Please log in to xiaohongshu.com in your browser first.", "ERROR")
            raise SystemExit(1)

        log(f"  Extracted {len(self.cookies)} cookies")

    # ── HTTP client setup ──

    def _setup_http_client(self):
        self.http_client = httpx.AsyncClient(
            headers={
                "user-agent": USER_AGENT,
                "referer": f"https://{XHS_DOMAIN}/",
                "origin": f"https://{XHS_DOMAIN}",
            },
            cookies=self.cookies,
            timeout=30.0,
            follow_redirects=True,
        )
        log("HTTP client ready")

    # ── Fetch page data ──

    async def _fetch_page_data(self):
        """Fetch page HTML and extract __INITIAL_STATE__ JSON."""
        log("Fetching page data...")
        resp = await self.http_client.get(self.url)

        if resp.status_code != 200:
            log(f"Page returned HTTP {resp.status_code}", "ERROR")
            raise SystemExit(1)

        html = resp.text

        # Extract __INITIAL_STATE__ JSON
        m = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?})\s*</script>', html, re.DOTALL)
        if not m:
            # Try alternate pattern (some pages use different format)
            m = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.+?})\s*;?\s*(?:</script>|$)', html, re.DOTALL)

        if not m:
            log("Cannot find __INITIAL_STATE__ in page HTML", "ERROR")
            log("The page may require login or the format has changed", "ERROR")
            raise SystemExit(1)

        raw_json = m.group(1)
        # Xiaohongshu uses 'undefined' in JSON which is invalid — replace with null
        raw_json = re.sub(r'\bundefined\b', 'null', raw_json)

        try:
            state = json.loads(raw_json)
        except json.JSONDecodeError as e:
            log(f"Failed to parse __INITIAL_STATE__ JSON: {e}", "ERROR")
            raise SystemExit(1)

        log("  __INITIAL_STATE__ extracted successfully")
        return state

    # ── Parse note data ──

    def _parse_note_data(self, state):
        """Extract note info from __INITIAL_STATE__ JSON."""
        log("Parsing note data...")

        note_data = None

        # Try known path: state.note.noteDetailMap[noteId].note
        try:
            note_detail_map = state.get("note", {}).get("noteDetailMap", {})
            if self.note_id in note_detail_map:
                note_data = note_detail_map[self.note_id].get("note")
            else:
                # Try first available entry
                for key, val in note_detail_map.items():
                    if isinstance(val, dict) and "note" in val:
                        note_data = val["note"]
                        break
        except (AttributeError, TypeError):
            pass

        # Fallback: walk_find for object with imageList
        if not note_data:
            candidates = walk_find(state, lambda o: "imageList" in o and isinstance(o["imageList"], list))
            if candidates:
                note_data = candidates[0]

        if not note_data:
            log("Cannot find note data in __INITIAL_STATE__", "ERROR")
            log("The page structure may have changed", "ERROR")
            raise SystemExit(1)

        # Extract fields
        title = note_data.get("title", "").strip()
        desc = note_data.get("desc", "").strip()

        # Image list
        image_list = note_data.get("imageList", [])
        images = []
        for img in image_list:
            url = self._get_best_image_url(img)
            if url:
                images.append(url)

        if not images:
            log("No images found in note data", "ERROR")
            raise SystemExit(1)

        # User info
        user = note_data.get("user", {})
        author = user.get("nickname", user.get("nick_name", ""))
        user_id = user.get("userId", user.get("user_id", ""))

        # Time
        note_time = note_data.get("time", None)
        formatted_time = ""
        if note_time:
            try:
                # Timestamps can be in seconds or milliseconds
                ts = int(note_time)
                if ts > 1e12:
                    ts = ts / 1000
                dt = datetime.fromtimestamp(ts)
                formatted_time = dt.strftime("%Y-%m-%d %H:%M")
            except (ValueError, OSError):
                formatted_time = str(note_time)

        # If time is not in the standard field, try lastUpdateTime or ipLocation
        if not formatted_time:
            last_update = note_data.get("lastUpdateTime")
            if last_update:
                try:
                    ts = int(last_update)
                    if ts > 1e12:
                        ts = ts / 1000
                    dt = datetime.fromtimestamp(ts)
                    formatted_time = dt.strftime("%Y-%m-%d %H:%M")
                except (ValueError, OSError):
                    pass

        log(f"  Title: {title or '(none)'}")
        log(f"  Author: {author}")
        log(f"  Images: {len(images)}")

        return {
            "title": title,
            "desc": desc,
            "images": images,
            "author": author,
            "user_id": user_id,
            "time": formatted_time,
        }

    def _get_best_image_url(self, img_obj):
        """Extract the highest quality image URL from an image object."""
        # Try urlDefault first (usually high quality)
        url = img_obj.get("urlDefault", "")
        if not url:
            url = img_obj.get("url", "")
        if not url:
            # Try infoList for highest resolution
            info_list = img_obj.get("infoList", [])
            if info_list:
                # Pick the last one (usually highest res)
                url = info_list[-1].get("url", "")

        if not url:
            return None

        # Ensure https
        if url.startswith("//"):
            url = "https:" + url
        elif not url.startswith("http"):
            url = "https://" + url

        # Remove quality compression suffixes to get original quality
        # Common patterns: ?imageView2/2/w/1080/format/webp
        # We want the original, so strip imageView parameters
        url = re.sub(r'\?imageView2.*$', '', url)
        # Also strip imageMogr2 parameters
        url = re.sub(r'\?imageMogr2.*$', '', url)

        return url

    # ── Download images ──

    async def _download_images(self, image_urls):
        """Download all images concurrently to a temp directory."""
        log(f"Downloading {len(image_urls)} images...")
        tmp_dir = tempfile.mkdtemp(prefix="xhs_ocr_")

        async def download_one(idx, url):
            try:
                resp = await self.http_client.get(
                    url,
                    headers={"referer": f"https://{XHS_DOMAIN}/"},
                )
                if resp.status_code != 200:
                    log(f"  Image {idx+1} download failed: HTTP {resp.status_code}", "WARN")
                    return None

                # Determine extension from content-type or URL
                content_type = resp.headers.get("content-type", "")
                if "png" in content_type:
                    ext = ".png"
                elif "webp" in content_type:
                    ext = ".webp"
                else:
                    ext = ".jpg"

                path = os.path.join(tmp_dir, f"{idx+1:02d}{ext}")
                with open(path, "wb") as f:
                    f.write(resp.content)
                return path
            except Exception as e:
                log(f"  Image {idx+1} download error: {e}", "WARN")
                return None

        tasks = [download_one(i, url) for i, url in enumerate(image_urls)]
        results = await asyncio.gather(*tasks)

        paths = [p for p in results if p is not None]
        log(f"  Downloaded {len(paths)}/{len(image_urls)} images to {tmp_dir}")

        if not paths:
            log("No images downloaded successfully", "ERROR")
            raise SystemExit(1)

        return paths

    # ── OCR ──

    def _ocr_images(self, image_paths):
        """Run macOS Vision OCR via Swift helper."""
        log(f"Running OCR on {len(image_paths)} images...")

        script_dir = os.path.dirname(os.path.abspath(__file__))
        ocr_helper = os.path.join(script_dir, "ocr_helper.swift")

        if not os.path.exists(ocr_helper):
            log(f"OCR helper not found: {ocr_helper}", "ERROR")
            raise SystemExit(1)

        try:
            result = subprocess.run(
                ["swift", ocr_helper] + image_paths,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except subprocess.TimeoutExpired:
            log("OCR timed out after 120s", "ERROR")
            raise SystemExit(1)

        if result.returncode != 0:
            log(f"OCR failed (exit code {result.returncode})", "ERROR")
            if result.stderr:
                log(f"  stderr: {result.stderr[:500]}", "ERROR")
            raise SystemExit(1)

        # Split output by --- separator
        raw_output = result.stdout
        segments = raw_output.split("\n---\n")

        texts = []
        for seg in segments:
            text = seg.strip()
            texts.append(text)

        log(f"  OCR complete: {len(texts)} image(s) processed")
        return texts

    # ── Compose Markdown ──

    def _compose_markdown(self, note_meta, ocr_texts):
        """Combine OCR text and metadata into Markdown."""
        title = note_meta["title"]
        author = note_meta["author"]
        formatted_time = note_meta["time"]
        desc = note_meta["desc"]

        lines = []

        # Title
        if title:
            lines.append(f"# {title}")
        else:
            lines.append("# (Untitled)")

        lines.append("")

        # Meta line
        meta_parts = []
        if author:
            meta_parts.append(f"Author: {author}")
        if formatted_time:
            meta_parts.append(formatted_time)
        meta_parts.append(f"[Original]({self.url})")
        lines.append(f"> {' | '.join(meta_parts)}")
        lines.append("")

        # OCR text from each image
        for i, text in enumerate(ocr_texts):
            if not text:
                continue

            text_lines = text.split("\n")

            # Deduplicate: if first image's first line matches title
            if i == 0 and title and text_lines:
                first_line = text_lines[0].strip()
                if first_line == title or first_line in title or title in first_line:
                    text_lines = text_lines[1:]

            cleaned = "\n".join(text_lines).strip()
            if cleaned:
                lines.append(cleaned)
                lines.append("")

        # Description at bottom (if present and different from OCR content)
        if desc:
            lines.append("---")
            lines.append("")
            lines.append(desc)
            lines.append("")

        return "\n".join(lines)

    # ── Save output ──

    def _save_output(self, markdown, note_meta):
        """Save Markdown file."""
        os.makedirs(self.output_dir, exist_ok=True)

        title = note_meta.get("title", "")
        safe_title = sanitize_filename(title) if title else "untitled"
        filename = f"{safe_title}_{self.note_id}.md"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown)

        log(f"  Saved: {filepath}")
        print(f"\n{'=' * 50}")
        print(f"  Output: {filepath}")
        print(f"{'=' * 50}\n")

    # ── Cleanup ──

    async def _cleanup(self):
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
        description="Xiaohongshu Article to Markdown — CDP + HTTP + macOS Vision OCR",
    )
    parser.add_argument("url", help="Xiaohongshu post URL")
    parser.add_argument("--output-dir", default=".", help="Output directory (default: current dir)")
    parser.add_argument("--cdp-port", type=int, default=DEFAULT_CDP_PORT,
                        help=f"CDP debug port (default: {DEFAULT_CDP_PORT})")

    args = parser.parse_args()

    converter = XhsToMarkdown(
        url=args.url,
        output_dir=args.output_dir,
        cdp_port=args.cdp_port,
    )

    asyncio.run(converter.run())


if __name__ == "__main__":
    main()
