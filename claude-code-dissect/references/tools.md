# Tool System

## The Tool Interface (~30 methods)

```typescript
Tool<Input, Output, Progress> = {
  name, aliases?, searchHint?           // identity
  shouldDefer?, alwaysLoad?, isMcp?     // loading behavior
  inputSchema: lazySchema(() => z.strictObject({...}))  // LAZY Zod schema
  
  call(args, ctx, canUseTool, msg, onProgress) → ToolResult
  validateInput(input, ctx) → ValidationResult    // before permission
  checkPermissions(input, ctx) → { behavior: 'allow'|'deny'|'ask' }
  
  isConcurrencySafe(), isReadOnly(), isDestructive(), isEnabled()
  
  renderToolUseMessage()         // before execution
  renderToolUseProgressMessage() // during
  renderToolResultMessage()      // after
  renderGroupedToolUse()         // parallel group
  
  maxResultSizeChars: number     // threshold for disk persistence
  prompt() → string              // system prompt contribution
}
```

## LazySchema — Why and How

```typescript
// NOT this (created at import time, expensive):
const inputSchema = z.strictObject({ ... })

// THIS (created on first access):
const inputSchema = lazySchema(() => z.strictObject({ ... }))

// Benefits: dead code elimination behind feature flags,
// faster module load, breaks circular imports
```

## Tool Registration Pipeline

```
getAllBaseTools() → static list + feature-gated conditionals
  ↓ getTools(permCtx) → simple mode filter + deny rules + isEnabled()
  ↓ assembleToolPool(permCtx, mcpTools)
    → sort EACH list by name (prompt cache stability!)
    → deduplicate (built-in wins)
    → return: built-ins ++ mcpTools (contiguous prefix)
```

## Execution Pipeline (10 steps)

```
1. JSON parse from streaming accumulator
2. Zod schema validation
3. tool.validateInput()
4. tool.checkPermissions() → allow/deny/ask
5. If ask: PermissionRequest hooks (can modify input!)
6. If still ask: prompt user or run AI classifier
7. PreToolUse hooks
8. tool.call()
9. PostToolUse hooks (or PostToolUseFailure)
10. If result > maxResultSizeChars → persist to disk, replace with path
```

## Tool Deferral (ToolSearch)

Problem: 100+ tools × ~500 tokens = 50K+ in prompt.
Solution: `shouldDefer: true` → excluded from initial prompt. Model calls `ToolSearch("keyword")` → returns matching names → model calls those tools. Saves ~60-70% tokens.

## Result Persistence

Each tool declares `maxResultSizeChars`. FileReadTool = Infinity (never persist, would loop). If exceeded → write to temp file → replace result with file path.

## Bash Parser (Security Engine)

`utils/bash/bashParser.ts` (4436 lines): full Bash AST parser.
Pipeline: tokenize → AST → classify (read-only/write/dangerous via commands.ts) → path validation → permission decision.
`bashPermissions.ts` (2621 lines): command-level matching against rules.
`bashSecurity.ts` (2592 lines): injection detection.

## Reading Order

1. `Tool.ts` — complete interface
2. `tools.ts` — registration, assembleToolPool()
3. `services/tools/toolExecution.ts` lines 1-400 — pipeline
4. `tools/BashTool/BashTool.tsx` — complex tool reference
5. `tools/FileReadTool/FileReadTool.ts` — clean read-only example
6. `utils/toolSearch.ts` — deferred discovery
7. `utils/toolResultStorage.ts` — result persistence

## Files

| File | Lines | What to read for |
|------|-------|------------------|
| `Tool.ts` | 792 | Complete tool contract |
| `tools.ts` | 389 | Registration, sorting, dedup |
| `services/tools/toolExecution.ts` | 1745 | 10-step execution |
| `utils/toolResultStorage.ts` | 1040 | Large result persistence |
| `utils/toolSearch.ts` | 756 | Deferred tool discovery |
| `tools/BashTool/BashTool.tsx` | 1143 | Complex tool impl |
| `tools/BashTool/bashPermissions.ts` | 2621 | Command permission matching |
| `tools/BashTool/bashSecurity.ts` | 2592 | Security analysis |
| `utils/bash/bashParser.ts` | 4436 | Full Bash AST parser |
| `utils/bash/ast.ts` | 2679 | AST node definitions |

## Neighbors

← `engine.md` (engine triggers tool execution)
→ `permissions.md` (tools call checkPermissions)
→ `hooks.md` (PreToolUse/PostToolUse wrap call)
→ `agents.md` (AgentTool spawns sub-agents)
→ `extensions.md` (MCPTool wraps MCP, SkillTool executes skills)
