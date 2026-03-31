# Memory System (3 Layers)

## Layer 1: Auto Memory (cross-session)

```
Location: ~/.claude/projects/<slug>/memory/
Index: MEMORY.md (200 line cap, 25KB max)
  Format: "- [Title](file.md) — one-line hook"
  Always loaded into conversation context.

Topic files: YAML frontmatter + markdown
  ---
  name: Memory Name
  description: one-line (for relevance matching)
  type: user|feedback|project|reference
  ---
  Content here.

Types:
  user      → role, preferences (tailor behavior)
  feedback  → corrections + confirmations (approach guidance)
  project   → decisions not in code (motivations)
  reference → external system pointers (dashboards, channels)

NOT saved: code patterns, git history, debug solutions, ephemeral state
```

## Layer 2: Session Memory (per-conversation)

```
Location: .claude/projects/<slug>/session-memory/<sessionId>.md
Trigger: token threshold (~10K) + tool call interval (≥3) + natural break
Process: forked agent → read conversation → write summary (Edit tool only)
Use: re-injected during compaction for continuity
Manual: /summary command bypasses thresholds
```

## Layer 3: Agent Memory (per-type, scoped)

```
user:    ~/.claude/agent-memory/<agentType>/
project: .claude/agent-memory/<agentType>/
local:   .claude/agent-memory-local/<agentType>/
Same MEMORY.md + topic files format. Directory auto-created.
```

## Auto Extraction Pipeline

```
Trigger: end of query loop (no tool calls in response), every N turns
Skip if: main agent already wrote to memory this turn

extractMemories.ts:
  1. Spawn forked agent (shares parent's prompt cache)
  2. System prompt: "analyze conversation for memorable facts"
  3. Existing memories injected as manifest (avoids ls turn)
  4. Tool restrictions: Read/Grep/Glob unrestricted, Bash read-only, Edit/Write ONLY for memory paths
  5. Max 5 turns (hard cap)
  6. Cursor: lastMemoryMessageUuid advances only on success
```

## Team Memory Sync

```
Shared: .claude/agent-memory/team/ (version-controlled)
Sync: file watcher detects changes → other teammates notified → memory re-loaded
```

## Where Memories Appear

1. MEMORY.md → AttachmentMessage at conversation start
2. Session memory → used during compaction (re-injected as knowledge)
3. Agent memory → appended to agent's system prompt via loadAgentMemoryPrompt()

## Reading Order

1. `memdir/memdir.ts` — MEMORY.md format, read/write
2. `services/extractMemories/extractMemories.ts` — auto extraction
3. `services/SessionMemory/sessionMemory.ts` — session summarization
4. `services/teamMemorySync/index.ts` — team sync

## Files

| File | Lines | What to read for |
|------|-------|------------------|
| `memdir/memdir.ts` | 507 | Index management, topic file format |
| `services/extractMemories/extractMemories.ts` | 615 | Auto extraction pipeline |
| `services/SessionMemory/sessionMemory.ts` | 495 | Session summarization |
| `services/teamMemorySync/index.ts` | 1256 | Team memory sync |
| `services/compact/sessionMemoryCompact.ts` | 630 | Memory during compaction |

## Neighbors

← `context.md` (compaction triggers session memory extraction)
← `agents.md` (agents have scoped memory)
→ `engine.md` (MEMORY.md injected at conversation start)
