# Conversation Engine

## The Main Loop — 4 Stages

```
STAGE 1: MESSAGE PREPARATION (handlePromptSubmit.ts)
  Build UserMessage from input → attach images/files → process slash commands

STAGE 2: API CALL (query.ts → services/api/claude.ts)
  normalizeMessagesForAPI()
    strip virtual messages, merge consecutive same-role, ensure tool_use↔tool_result pairing
  buildEffectiveSystemPrompt()
  Build tool schemas (assembleToolPool)
  anthropic.beta.messages.create({ stream: true })

STAGE 3: STREAM PROCESSING (queryModelWithStreaming — async generator)
  yield: content_block_start → content_block_delta → content_block_stop → message_stop
  withRetry(): 429→wait+retry, 5xx→retry, prompt_too_long→compact+retry, 529→model fallback

STAGE 4: TOOL EXECUTION (services/tools/toolExecution.ts)
  for each tool_use block:
    Zod validate → validateInput → checkPermissions → PreToolUse hooks
    → tool.call() → PostToolUse hooks → generate tool_result
    → if result > maxResultSizeChars → persist to disk
  stop_reason=tool_use → loop back to STAGE 2
  stop_reason=end_turn → done, await user input
```

## Key Abstractions

**queryModelWithStreaming()**: async generator yielding stream events. Handles system prompt, tools, cache control, thinking, betas.

**withRetry()**: exponential backoff for 429/5xx, drops oldest messages for prompt_too_long, circuit breaker (max 3 compact retries), model fallback on 529.

**normalizeMessagesForAPI()**: the critical sanitizer. Removes virtual messages, merges consecutive user messages (Bedrock compatibility), ensures tool_use/tool_result pairing.

**ToolUseContext**: execution environment passed to every tool — tools, abortController, readFileState, getAppState/setAppState, messages, agentId, resource limits.

**Streaming architecture**: text streams in real-time (character by character), but tool execution only starts after the model finishes the tool_use block (needs complete JSON).

## Reading Order

1. `utils/handlePromptSubmit.ts` — follow user message from input to API
2. `query.ts` lines 1-200 — main query loop structure
3. `services/api/claude.ts` lines 750-1020 — queryModelWithStreaming()
4. `services/api/withRetry.ts` lines 1-200 — retry strategy
5. `utils/messages.ts` lines 1989-2300 — normalizeMessagesForAPI()
6. `services/tools/toolExecution.ts` lines 1-400 — tool execution pipeline

## Files

| File | Lines | What to read for |
|------|-------|------------------|
| `query.ts` | 1729 | Main query loop, continue/stop |
| `QueryEngine.ts` | 1295 | Query state machine, interrupts |
| `services/api/claude.ts` | 3419 | API call, streaming, cache control |
| `services/api/withRetry.ts` | 822 | Retry strategies, error classification |
| `services/api/client.ts` | 389 | Anthropic SDK client setup |
| `services/api/errors.ts` | 1207 | Error taxonomy |
| `utils/messages.ts` | 5512 | Message normalization, pairing |
| `utils/handlePromptSubmit.ts` | 610 | User input → message construction |
| `services/tools/toolExecution.ts` | 1745 | Tool execution pipeline |

## Neighbors

← `bootstrap.md` (engine starts after bootstrap)
→ `tools.md` (engine invokes tools via toolExecution)
→ `context.md` (engine calls buildEffectiveSystemPrompt before each API call)
→ `permissions.md` (tool execution checks permissions)
→ `hooks.md` (PreToolUse/PostToolUse fire during execution)
