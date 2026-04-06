# podcast-to-md Design Spec

## Purpose

A Claude Code skill that turns Apple Podcasts into rich, structured Markdown files — not as a one-shot converter, but as a **data asset generator**. Each output `.md` is a self-contained knowledge unit with maximum structured metadata, designed to support future transformations: summarization, topic extraction, quote mining, search/retrieval, knowledge graphs, newsletter generation, etc.

## Architecture

```
podcast-to-md/
├── SKILL.md              # Workflow definition for Claude (the orchestrator)
├── scripts/
│   ├── search            # iTunes Search API → JSON
│   ├── episodes          # RSS parsing + time filtering + transcript probe → JSON
│   └── transcribe        # Local faster-whisper → timestamped text
```

### Design Principles

1. **Claude is the orchestrator.** SKILL.md defines the workflow. Claude calls scripts, makes decisions, handles errors, renders output. Scripts are tools, not the brain.
2. **Scripts do what Claude can't.** Call APIs, parse XML, run ML models. Each script does one thing and outputs structured data.
3. **Claude does what it's best at.** Rendering Markdown, formatting frontmatter, asking the user, adapting to edge cases.
4. **Maximize structured information.** Every piece of metadata from RSS gets captured. Transcripts preserve timestamps. Nothing is thrown away.
5. **Output is raw material.** The Markdown files are meant to be consumed by agents and tools downstream, not just read by humans.

## Scripts

### `search`

**Purpose:** Find podcasts on Apple Podcasts.

**Input:**
- Positional: query string (podcast name) OR Apple Podcasts URL/ID
- `--limit N`: max results (default: 5)

**Output:** JSON array to stdout.

```json
[
  {
    "id": 1553186028,
    "name": "硬地骇客",
    "artist": "硬地骇客",
    "rss_url": "https://feed.example.com/podcast.xml",
    "artwork_url": "https://...",
    "genre": "Technology",
    "episode_count": 142,
    "language": "zh",
    "last_updated": "2024-03-15"
  }
]
```

**Implementation:**
- iTunes Search API: `https://itunes.apple.com/search?term=...&media=podcast`
- Apple Podcasts URL: extract ID, use Lookup API: `https://itunes.apple.com/lookup?id=...`
- `feedUrl` field from iTunes response gives the RSS URL

**Dependencies:** `requests`

### `episodes`

**Purpose:** Parse a podcast RSS feed, filter by time range, and extract maximum metadata per episode. Probe for existing transcript URLs.

**Input:**
- Positional: RSS feed URL
- `--from YYYY-MM[-DD]`: start date (inclusive)
- `--to YYYY-MM[-DD]`: end date (inclusive)
- `--recent N`: last N episodes
- `--all`: all episodes
- (no filter defaults to `--recent 10`)

**Output:** JSON object to stdout.

```json
{
  "podcast": {
    "title": "硬地骇客",
    "description": "...",
    "language": "zh",
    "author": "...",
    "link": "https://...",
    "artwork_url": "https://...",
    "categories": ["Technology", "Entrepreneurship"]
  },
  "episodes": [
    {
      "title": "EP42: 独立开发者的困境",
      "description": "<p>Show notes HTML...</p>",
      "date": "2024-03-15",
      "duration": "01:23:45",
      "season": 2,
      "episode": 42,
      "explicit": false,
      "audio_url": "https://...",
      "episode_url": "https://...",
      "artwork_url": "https://...",
      "transcript_url": null,
      "transcript_type": null,
      "chapters_url": null,
      "keywords": ["独立开发", "创业"],
      "summary": "..."
    }
  ],
  "total_count": 142,
  "filtered_count": 15
}
```

**Transcript URL detection:**
- Check `<podcast:transcript>` tag (Podcasting 2.0 namespace)
- Check `<enclosure>` with transcript MIME types
- Report `transcript_type`: "srt", "vtt", "json", "text", or null

**Implementation notes:**
- Parse RSS with `feedparser`
- iTunes namespace (`itunes:duration`, `itunes:season`, `itunes:episode`, `itunes:explicit`, `itunes:keywords`, `itunes:summary`, `itunes:image`)
- Podcasting 2.0 namespace (`podcast:transcript`, `podcast:chapters`)
- Duration normalization: handle both "HH:MM:SS" and seconds-only formats

**Dependencies:** `feedparser`, `requests`

### `transcribe`

**Purpose:** Transcribe a podcast audio file using local faster-whisper model.

**Input:**
- Positional: audio URL or local file path
- `--model`: whisper model size (default: `medium`)
- `--language`: language hint (optional, auto-detect if omitted)

**Output:** Timestamped transcript to stdout, one segment per line.

```
[00:00:00] 大家好，欢迎收听硬地骇客。
[00:00:05] 今天我们聊一个话题，独立开发者的困境。
[00:01:23] 我先介绍一下今天的嘉宾...
```

**Implementation:**
- Download audio to temp file if URL provided
- Run faster-whisper with specified model
- Output `[HH:MM:SS] text` format, one segment per line
- Print progress to stderr (model loading, transcription %)

**Dependencies:** `faster-whisper`, `requests`

**First-run:** faster-whisper auto-downloads the model on first use (~1-3GB depending on size). The script should inform the user via stderr.

## Workflow (defined in SKILL.md)

SKILL.md tells Claude to follow these steps:

### Step 1: Identify the podcast

- If user gives a name → run `search "name"` → if multiple results, ask user to pick
- If user gives an Apple Podcasts URL → run `search "URL"` → should return exactly one result
- Confirm the podcast with the user (show name, artist, episode count)

### Step 2: Get episode list

- Run `episodes <rss_url>` with the user's time filter (`--from`/`--to`, `--recent`, `--all`)
- Show the user a summary: N episodes found, date range, total duration
- Ask user to confirm before proceeding

### Step 3: Process episodes

For each episode, in chronological order:

1. **Try existing transcript first:**
   - If `transcript_url` is present, fetch it (WebFetch or curl)
   - Parse SRT/VTT into `[HH:MM:SS] text` format
2. **Fallback to Whisper:**
   - If no transcript available, run `transcribe <audio_url>`
   - Report progress to user

3. **Generate the episode `.md` file:**
   Claude renders the Markdown with:

   ```markdown
   ---
   title: "EP42: 独立开发者的困境"
   podcast: "硬地骇客"
   date: 2024-03-15
   duration: "01:23:45"
   season: 2
   episode: 42
   explicit: false
   source: apple-transcript | rss-transcript | whisper
   audio_url: "https://..."
   episode_url: "https://..."
   artwork_url: "https://..."
   categories:
     - Technology
     - Entrepreneurship
   keywords:
     - 独立开发
     - 创业
   guests: []
   ---

   ## Show Notes

   [RSS description content, preserved as-is with HTML converted to Markdown]

   ## Transcript

   [00:00:00] 大家好，欢迎收听硬地骇客。
   [00:00:05] 今天我们聊一个话题...

   ## Links

   - [Link text](URL) — extracted from show notes
   ```

4. **File naming:** `YYYY-MM-DD-episode-slug.md` (date + slugified title)
5. **Output directory:** user-specified or `./podcast-transcripts/<podcast-slug>/`

### Step 4: Generate index.md

Claude generates an index file:

```markdown
---
type: podcast-index
podcast: "硬地骇客"
artist: "硬地骇客"
language: zh
categories:
  - Technology
  - Entrepreneurship
episode_count: 15
date_range:
  from: 2024-01-15
  to: 2024-06-20
total_duration: "18:45:30"
generated: 2026-04-07
sources:
  apple-transcript: 8
  rss-transcript: 2
  whisper: 5
---

# 硬地骇客 — Transcript Index

| # | Date | Title | Duration | Source | File |
|---|------|-------|----------|--------|------|
| 42 | 2024-03-15 | 独立开发者的困境 | 01:23:45 | whisper | [link](./2024-03-15-ep42-独立开发者的困境.md) |
| ... | ... | ... | ... | ... | ... |

## Statistics

- Total episodes: 15
- Total duration: 18h 45m 30s
- Transcript sources: 8 Apple, 2 RSS, 5 Whisper
- Date range: 2024-01-15 to 2024-06-20
```

### Step 5: Report completion

Claude summarizes what was done: episodes processed, transcription sources breakdown, output directory, any failures.

## Error Handling (Claude's responsibility)

- **Network errors:** Retry once, then report and skip the episode
- **Whisper model download:** Inform user on first run, ask to proceed
- **Transcript parsing errors:** Fall back to Whisper, report the fallback
- **Empty episodes:** Skip, note in index
- **Rate limiting:** Pause and retry

## Future Extensions (not in scope now, but the data supports them)

- Speaker diarization (add `speakers` to frontmatter, `[Speaker A]` tags in transcript)
- Topic/chapter extraction from transcript
- Cross-episode search and knowledge graph
- Summary generation per episode
- Newsletter/digest generation from recent episodes
