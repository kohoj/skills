# Gateway: Multi-Platform Messaging

## Architecture — 14 Platform Adapters

```
GatewayRunner (gateway/run.py, 6387 lines)
  |
  +-> GatewayConfig (config.yaml + env vars + gateway.json)
  +-> SessionStore (SQLite + legacy JSONL)
  +-> DeliveryRouter (origin, local, platform:chat_id)
  +-> HookRegistry (gateway:startup, session:*, agent:*, command:*)
  +-> Platform Adapters:
      telegram, discord, feishu, slack, wecom, whatsapp,
      signal, matrix, mattermost, dingtalk, email, sms,
      webhook, api_server, homeassistant
```

## Message Flow (7 stages)

```
STAGE 1: AUTHORIZATION
  Unauthorized DM -> generate pairing code (rate-limited)
  Unauthorized group -> silently ignore

STAGE 2: INTERRUPT CHECK (if agent running for session)
  /stop  -> hard-kill agent, unlock session
  /new   -> interrupt + reset session
  /queue -> queue without interrupt
  PHOTO  -> queue without interrupt (photo burst batching)
  Other  -> interrupt with priority

STAGE 3: COMMAND DISPATCH
  /new, /reset -> session reset
  /voice -> toggle auto-TTS
  /compress, /retry, /undo -> session manipulation
  /approve, /deny -> exec approvals
  Other -> user-defined quick_commands

STAGE 4: SESSION MANAGEMENT
  SessionStore.get_or_create_session(session_key)
  Evaluate reset policy (daily | idle | both | none)
  Load transcript from SQLite or JSONL (prefers longer source)

STAGE 5: CONTEXT BUILDING
  Build SessionContext (source + connected platforms + home channels)
  Generate system prompt with session_context_prompt
  PII redaction if enabled (Telegram, WhatsApp, Signal only)

STAGE 6: AGENT EXECUTION
  Get or create cached AIAgent (preserves prefix cache across messages)
  Set _AGENT_PENDING_SENTINEL in _running_agents
  Run agent via _handle_message_with_agent()

STAGE 7: RESPONSE DELIVERY
  extract_images() -> markdown/HTML image URLs
  extract_media() -> MEDIA: tags, [[audio_as_voice]]
  extract_local_files() -> bare file paths (avoids code blocks)
  _send_with_retry() -> exponential backoff, plain-text fallback
```

## Platform Adapter Pattern

```python
class BasePlatformAdapter:                   # 1519 lines
    async def connect() -> bool              # Auth + start receiving
    async def disconnect()                   # Clean shutdown
    async def send(chat_id, content) -> SendResult
    async def get_chat_info(chat_id) -> Dict

    # Built-in: media caching, retry logic, interrupt support
    # Built-in: image/audio/document extraction from responses
    # Built-in: human-like pacing (delays between text and media)
```

Each adapter: handles platform-specific auth, message formatting, threading (topics, threads, channels), media upload/download, rate limiting, auto-reconnect.

## Session Reset Policy

```
Mode: "daily" -> reset at specified hour (default 4am)
Mode: "idle"  -> reset after N minutes inactivity (default 1440=24h)
Mode: "both"  -> whichever triggers first
Mode: "none"  -> never auto-reset

Per-platform/type overrides:
  reset_by_type: { dm: {idle: 480}, group: {daily: 6} }
  reset_by_platform: { telegram: {mode: "none"} }

On auto-reset: background flush saves memories before context loss
  -> _flush_memories_for_session() extracts + persists
```

## Session Key Formula

```
f"agent:main:{platform}:{chat_type}:{chat_id}[:{thread_id}][:{user_id}]"

Per-user in groups: 3 participants -> 3 isolated sessions (if group_sessions_per_user=true)
Per-thread: Telegram topics, Discord threads, Slack threads are separate
```

## Reading Order

1. `gateway/config.py` lines 51-411 — Platform enum, GatewayConfig structure
2. `gateway/session.py` lines 422-462 — build_session_key()
3. `gateway/session.py` lines 590-632 — _should_reset() policy evaluation
4. `gateway/platforms/base.py` lines 403-1349 — BasePlatformAdapter
5. `gateway/run.py` lines 1686-2080 — _handle_message() main pipeline
6. `gateway/delivery.py` — DeliveryTarget, routing (351 lines, read all)
7. `gateway/hooks.py` — HookRegistry (170 lines, read all)

## Files

| File | Lines | What to read for |
|------|-------|------------------|
| `gateway/run.py` | 6387 | GatewayRunner lifecycle, message pipeline |
| `gateway/config.py` | 912 | Platform enum, config layering, reset policy |
| `gateway/session.py` | 1061 | Session keys, reset evaluation, PII redaction |
| `gateway/delivery.py` | 351 | Routing specs, local logging, truncation |
| `gateway/hooks.py` | 170 | Event types, wildcard matching, discovery |
| `gateway/platforms/base.py` | 1519 | Adapter interface, media extraction, retry |
| `gateway/platforms/telegram.py` | 2128 | MarkdownV2, forum topics, photo bursts |
| `gateway/platforms/discord.py` | 2300 | Voice capture, thread auto-archive, reactions |
| `gateway/platforms/feishu.py` | 3255 | Rich text, card buttons, serial queue |

## Neighbors

← `bootstrap.md` (gateway started via CLI dispatcher)
→ `engine.md` (each message spawns AIAgent.run_conversation)
→ `memory.md` (session reset triggers memory flush)
→ `integrations.md` (gateway uses send_message_tool for cross-platform)
