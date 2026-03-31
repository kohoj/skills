# Bootstrap, State & Infrastructure

## Boot Sequence (5 phases)

```
Phase 0: cli.tsx — zero-import fast paths
  --version → stdout.write(VERSION); exit(0)  // NO module load
  --daemon/--bridge → route to special handler
  startCapturingEarlyInput() → buffer keystrokes during load

Phase 1: dynamic import('./main.tsx') — heavy modules load here (~150ms)

Phase 2: init() via preAction hook (~100ms, memoized — runs once)
  enableConfigs()           → validate settings.json
  applySafeEnvVars()        → non-sensitive env only
  applyExtraCACerts()       → TLS certs (Bun caches at boot!)
  configureGlobalMTLS()     → client certs
  configureGlobalAgents()   → HTTP proxy agents
  preconnectAnthropicApi()  → TCP+TLS warmup (fire-and-forget, overlaps module load)
  async fire-and-forget: OAuth, JetBrains detection, git repo detection, remote settings

Phase 3: Commander.js program.parseAsync(process.argv)

Phase 4: replLauncher.tsx → dynamic import App+REPL → Ink render loop
```

**Key principles**: zero-import fast paths, dynamic import everything heavy, fire-and-forget async for non-critical init, API preconnect overlaps with module loading.

## Global State — The "Leaf Module" Pattern

`bootstrap/state.ts` is the most important architectural decision:
- Imports NOTHING (zero dependencies) → any module can safely import it
- ~150 getter/setter pairs for all session state
- Created once at module load via getInitialState()
- Categories: session identity, model config, cost tracking, permission state, telemetry, plugin/skill tracking, MCP config

## Session Persistence

Conversations stored as JSONL: `~/.claude/projects/<slug>/sessions/<sessionId>.jsonl`
Each line = one message. Recovery: load JSONL → rebuild message array → resume.

## Reading Order

1. `entrypoints/cli.tsx` — boot routing, fast paths
2. `entrypoints/init.ts` — init() function, parallel prefetch
3. `bootstrap/state.ts` — skip to getInitialState() and getter/setter pairs
4. `main.tsx` lines 585-950 — preAction hook and CLI setup
5. `replLauncher.tsx` — REPL launch point
6. `utils/sessionStorage.ts` lines 1-200 — JSONL format
7. `utils/worktree.ts` — git worktree isolation (if relevant)

## Files

| File | Lines | What to read for |
|------|-------|------------------|
| `entrypoints/cli.tsx` | ~720 | Boot routing, fast paths, early input capture |
| `entrypoints/init.ts` | 340 | Init sequence, memoization, parallel prefetch |
| `bootstrap/state.ts` | 1758 | Leaf module pattern, state getter/setter design |
| `main.tsx` | 4683 | CLI parsing, preAction hook (line 907+) |
| `replLauncher.tsx` | ~23 | Dynamic component import |
| `utils/sessionStorage.ts` | 5105 | JSONL transcript, session indexing |
| `utils/sessionRestore.ts` | 551 | Conversation recovery |
| `utils/gracefulShutdown.ts` | 529 | Cleanup handler registration |
| `utils/worktree.ts` | 1519 | Git worktree create/cleanup |
| `utils/git.ts` | 926 | Branch, status, commit |

## Neighbors

→ `engine.md` (after bootstrap, control flows to query engine)
→ `context.md` (init sets up state that context assembly reads)
→ `extensions.md` (plugin/MCP init during bootstrap)
