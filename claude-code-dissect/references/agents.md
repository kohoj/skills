# Multi-Agent System

## 3 Spawn Modes

```
Mode 1: SYNC (default, run_in_background: false)
  runAgent() generator → collect messages → return { status: 'completed', result }
  Parent waits.

Mode 2: ASYNC (run_in_background: true)
  New unlinked AbortController → spawn LocalAgentTask → return { status: 'async_launched', agentId }
  Parent continues. Result via TaskOutput tool.

Mode 3: TEAMMATE (swarm)
  spawnTeammate() → detect backend → split pane or in-process → independent execution
  Communication via file mailbox.
```

## Fork Subagent — Prompt Cache Optimization

The key multi-agent cost innovation:
```
Fork child inherits parent's FULL conversation context (byte-identical)
→ API request prefix is identical → prompt cache HIT → ~90% token savings

Implementation:
  1. Clone parent's assistant message (all tool_use + thinking)
  2. Single user message with placeholder tool_results + per-child directive
  3. Guard: <fork_boilerplate_tag> prevents recursive forks
  4. useExactTools=true → skip tool resolution (byte-identical)

Directive: XML-wrapped, strict rules (no questions, no sub-agents, ≤500 words)
```

## Swarm Backends

```
registry.ts: detectAndGetBackend()
  iTerm2 → ITermBackend (Python API, native split panes)
  tmux   → TmuxBackend (split-panes, leader left / teammates right)
  else   → InProcessBackend (AsyncLocalStorage isolation, no terminal)

InProcessBackend (most interesting for borrowing):
  spawn() → TeammateContext (agentName, teamName, color, AbortController)
  startInProcessTeammate() → fire-and-forget main loop:
    process prompt → query loop → mark idle → poll mailbox (500ms)
    → new message: run again → shutdown request: abort → idle: tryClaimNextTask()
```

## File Mailbox IPC

```
Directory: .claude/projects/<slug>/team/<teamName>/<agentName>/
Messages: timestamped JSON files, read tracking via sidecar .read file
Types: DM, idle notification, shutdown request (highest priority), permission req/resp
Poll: 500ms interval, process by priority
```

## Context Isolation

```
readFileState:           CLONED to child
contentReplacementState: SHARED (for prompt cache stability)
abortController:         SHARED (sync) or NEW (async)
setAppState:             SHARED (sync) or ISOLATED (async)
MCP clients:             parent's (default) or agent-specific
AsyncLocalStorage:       per-teammate isolation (in-process)
```

## Reading Order

1. `tools/AgentTool/AgentTool.tsx` — 3-mode dispatch
2. `tools/AgentTool/runAgent.ts` — execution lifecycle, cleanup
3. `utils/forkedAgent.ts` — fork cache pattern
4. `tools/shared/spawnMultiAgent.ts` — spawnTeammate(), backend detection
5. `utils/swarm/backends/InProcessBackend.ts` — in-process execution
6. `utils/swarm/inProcessRunner.ts` — teammate main loop
7. `utils/teammateMailbox.ts` — file-based IPC
8. `utils/swarm/permissionSync.ts` — teammate→leader permission bridge

## Files

| File | Lines | What to read for |
|------|-------|------------------|
| `tools/AgentTool/AgentTool.tsx` | 1397 | 3-mode entry point |
| `tools/AgentTool/runAgent.ts` | 973 | Execution, isolation, cleanup |
| `utils/forkedAgent.ts` | 689 | Fork for cache sharing |
| `tools/shared/spawnMultiAgent.ts` | 1093 | Teammate spawn, backend detect |
| `utils/swarm/inProcessRunner.ts` | 1552 | In-process main loop |
| `utils/swarm/permissionSync.ts` | 928 | Permission bridge |
| `utils/swarm/backends/InProcessBackend.ts` | 339 | Same-process backend |
| `utils/swarm/backends/TmuxBackend.ts` | 764 | Terminal pane management |
| `utils/teammateMailbox.ts` | 1183 | File-based IPC |
| `coordinator/coordinatorMode.ts` | 369 | Coordinator dispatch |

## Neighbors

← `tools.md` (AgentTool invoked by tool pipeline)
→ `memory.md` (agents have scoped memory)
→ `permissions.md` (teammate permissions bridged to leader)
→ `context.md` (fork agents share prompt for cache)
