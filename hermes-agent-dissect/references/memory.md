# Memory, Persistence & Sessions

## 3-Layer Memory Architecture

```
Layer 1: Memory Tool (curated, user-facing)
  tools/memory_tool.py — MemoryStore
  Bounded dual-target storage with file persistence
  § (section sign) delimiter for multiline entries
  Frozen snapshot pattern: system prompt loads at session start, never mutates
  -> writes update disk immediately, but prompt stays stable (prefix cache safe)

Layer 2: Honcho Integration (AI-native, cross-session)
  tools/honcho_tools.py — optional Honcho API client
  Functions: honcho_context, honcho_profile, honcho_search, honcho_conclude
  Persists insights/profiles across sessions
  Dialectic: multi-turn conversation with memory subsystem
  Per-turn injection: context appended as ephemeral message (not in history)

Layer 3: Session Storage (transcript-level)
  ~/.hermes/sessions/{session_id}/
  SQLite database + legacy JSONL fallback
  Resumable from CLI: session browser with live search
  Full-text search via session_search_tool
```

## Memory Tool — Frozen Snapshot Pattern

```python
class MemoryStore:                          # 549 lines
    load_from_disk():
      Read entries -> capture frozen snapshot for system prompt
      Snapshot is immutable for entire session

    add(content):
      Append with char limit enforcement
      Write to disk immediately
      System prompt unchanged (cache-safe)

    replace(old_substring, new_content):
      Targeted update via substring matching

    remove(substring):
      Delete via substring matching

    format_for_system_prompt():
      Return frozen snapshot (never mutated mid-session)

Security:
  Injection protection: scan content for prompt injection + exfiltration
  File locking: atomic rename (no truncate race) + separate lock files
```

## Honcho Memory Integration

```
AIAgent flow:
  1. _honcho_should_activate() -> check honcho_manager available
  2. _honcho_prefetch() -> fetch prior session context at turn start
  3. _inject_honcho_turn_context() -> append as ephemeral message
     (NOT in conversation history — keeps history clean for replay)
  4. Agent processes turn with enriched context
  5. _honcho_sync() -> save observations post-turn

Modes:
  honcho_context  -> recall from prior sessions
  honcho_profile  -> user/project profile management
  honcho_search   -> search across session history
  honcho_conclude -> extract and persist insights
```

## Session Persistence

```
Session storage (gateway/session.py):
  SessionStore backed by SQLite + JSONL fallback
  Load prefers longer source (SQLite vs JSONL)
  Per-session: messages, token counts, metadata

Session keys:
  "agent:main:{platform}:{chat_type}:{chat_id}[:{thread_id}][:{user_id}]"
  Deterministic key from SessionSource

Resume workflow:
  hermes sessions browse -> curses-based picker with search
  Load messages from DB -> hydrate TodoStore from history -> continue

Auto-reset (gateway):
  daily | idle | both | none policies
  Background flush: extract + persist memories before context loss
  Reset flags injected into system prompt: "Session was reset"
```

## Checkpoint System

```
tools/checkpoint_manager.py (548 lines):
  Snapshot/restore full execution state
  Used by RL training for rollback

  Max snapshots: 50 (configurable)
  Snapshot includes: messages, tool state, agent config
  Restore: hydrate agent from checkpoint, continue execution
```

## Todo Store (Ephemeral, Per-Session)

```
tools/todo_tool.py (268 lines):
  TodoStore — in-memory task list per agent loop
  Accessible via "todo" tool
  Cleared when agent completes
  Hydrated from message history on session resume
  Used by both CLI and gateway modes
```

## Session Search

```
tools/session_search_tool.py (504 lines):
  Full-text search across prior sessions
  Indexed by timestamp, content, metadata
  Returns relevant excerpts with context
  Used for cross-session knowledge retrieval
```

## Reading Order

1. `tools/memory_tool.py` lines 90-425 — MemoryStore, frozen snapshot
2. `tools/honcho_tools.py` lines 1-279 — Honcho tool functions
3. `run_agent.py` lines 342-370 — Honcho injection in agent loop
4. `gateway/session.py` lines 465-1028 — SessionStore, SQLite + JSONL
5. `tools/checkpoint_manager.py` lines 1-200 — snapshot/restore
6. `tools/session_search_tool.py` lines 1-200 — search interface

## Files

| File | Lines | What to read for |
|------|-------|------------------|
| `tools/memory_tool.py` | 549 | MemoryStore, frozen snapshot, injection protection |
| `tools/honcho_tools.py` | 279 | Honcho API: context, profile, search, conclude |
| `tools/todo_tool.py` | 268 | Ephemeral per-session task tracking |
| `tools/session_search_tool.py` | 504 | Cross-session full-text search |
| `tools/checkpoint_manager.py` | 548 | State snapshot/restore for RL |
| `gateway/session.py` | 1061 | SQLite + JSONL session store |
| `run_agent.py` | 8551 | Honcho prefetch/inject/sync (lines 342-370) |

## Neighbors

← `context.md` (frozen snapshot feeds into prompt cache stability)
← `engine.md` (Honcho sync happens post-turn in agent loop)
← `gateway.md` (session reset triggers memory flush)
→ `training.md` (checkpoints used for RL rollback)
