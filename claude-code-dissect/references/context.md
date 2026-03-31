# Context Management: Prompt Assembly, Compaction & Cache

## System Prompt — 5-Level Priority

```
Level 1 (highest): overrideSystemPrompt     → REPLACES ALL (loop mode)
Level 2: coordinatorSystemPrompt            → swarm coordinator mode
Level 3: agentSystemPrompt                  → subagent custom (append or replace)
Level 4: customSystemPrompt                 → --system-prompt CLI flag
Level 5: DEFAULT_SYSTEM_PROMPT              → standard prompt
Always: appendSystemPrompt                  → added after everything
```

Context sources injected alongside the prompt:
- `getSystemContext()` [per turn]: git status (branch, recent commits, uncommitted changes)
- `getUserContext()` [per conversation]: CLAUDE.md files (recursive discovery up dir tree) + current date
- Attachment messages: MEMORY.md, skills, MCP instructions, agent listings, deferred tools

CLAUDE.md discovery (`utils/claudemd.ts`): walks UP from cwd to root checking CLAUDE.md/.claude/CLAUDE.md, then DOWN into project subdirs. Merged with source headers. Respects .claudeignore.

## Context Compaction

```
Triggers:
  token_count > effective_window - 13K  → auto-compact
  API returns prompt_too_long           → reactive compact (drop oldest + retry)
  user runs /compact                    → manual

Pipeline:
  1. stripImagesFromMessages() → "[image]" markers
  2. stripReinjectedAttachments()
  3. Summarizer agent (NO tools, text-only, max 20K output):
     → structured summary: intent, concepts, files+snippets, errors, pending tasks, current work
  4. postCompactCleanup():
     re-inject top 5 file reads (≤5K each), invoked skills (≤25K total),
     reset deferred_tools/agent_listing/mcp_instructions deltas
  5. Extract session memory → persist to disk
  6. Insert SystemCompactBoundaryMessage
```

## Prompt Cache Strategy

```
Cache placement in API request:
  system[0]: cache_control { type: 'ephemeral', ttl: '5m' or '1h' }
  messages[-3]: cache_control (stable prefix)
  messages[-1]: cache_control (current turn)

Stability tactics:
  1. Tool list sorted alphabetically (tools.ts)
  2. Built-in tools as contiguous prefix before MCP tools
  3. Static system prompt parts placed before cache boundary
  4. Dynamic context (git, date) placed AFTER boundary
  5. microCompact.ts tracks edits to cached blocks

Cache break monitoring: promptCacheBreakDetection.ts watches cache_read_input_tokens
Cost impact: ~90% reduction when cache hits consistently
```

## Token Budget

```
effective = context_window - 20K (output reserve)
auto_compact = effective - 13K
blocking_limit = effective - 3K
estimation: roughTokenCountEstimation() ≈ char_count / 4 + 10% buffer
```

## Reading Order

1. `utils/systemPrompt.ts` — buildEffectiveSystemPrompt()
2. `context.ts` — getSystemContext(), getUserContext()
3. `utils/claudemd.ts` lines 1-400 — CLAUDE.md discovery
4. `services/compact/compact.ts` lines 1-500 — compaction pipeline
5. `services/compact/prompt.ts` — summarizer instructions
6. `services/compact/autoCompact.ts` — threshold calculation
7. `services/api/promptCacheBreakDetection.ts` lines 1-300 — cache diagnostics

## Files

| File | Lines | What to read for |
|------|-------|------------------|
| `utils/claudemd.ts` | 1479 | CLAUDE.md recursive discovery, merge |
| `constants/prompts.ts` | 914 | Hardcoded prompt templates |
| `services/compact/compact.ts` | 1705 | Full compaction pipeline |
| `services/compact/autoCompact.ts` | 351 | Thresholds, circuit breaker |
| `services/compact/prompt.ts` | 374 | Summarizer instructions |
| `services/compact/microCompact.ts` | 530 | Cache edit tracking |
| `services/api/promptCacheBreakDetection.ts` | 727 | Cache hit monitoring |
| `services/tokenEstimation.ts` | 495 | Token estimation |

## Neighbors

← `engine.md` (engine calls prompt assembly before each API call)
→ `memory.md` (compaction triggers session memory extraction)
→ `tools.md` (tool list sorting affects cache stability)
