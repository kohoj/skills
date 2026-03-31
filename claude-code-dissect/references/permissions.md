# Permission System

## 10-Step Decision Pipeline

```
hasPermissionsToUseToolInner(tool, input, context):

  1a. TOOL-LEVEL DENY — blanket deny rule? → DENY
  1b. TOOL-LEVEL ASK — blanket ask rule? → ASK
  1c. TOOL-SPECIFIC CHECK — tool.checkPermissions() (Bash parses command, File checks path)
  1d. TOOL DENIAL — checkPermissions returned 'deny'? → DENY
  1e. USER INTERACTION — tool.requiresUserInteraction()? → ASK (even in bypass!)
  1f. CONTENT-SPECIFIC ASK — match input against ask rules with ruleContent
  1g. SAFETY (bypass-immune!) — .git/, .claude/, .vscode/, shell configs → ASK always

  2a. MODE BYPASS — bypassPermissions mode? → ALLOW
  2b. ALLOW RULES — match against alwaysAllowRules → ALLOW

  3. PASSTHROUGH → ASK (default when nothing matched)
```

## Rule System

```
Rule = { source, ruleBehavior: 'allow'|'deny'|'ask', ruleValue: { toolName, ruleContent? } }
Sources (priority): policy > flag > user > project > local > cliArg > session

Matching:
  toolName: exact or alias, "mcp__serverName" matches all server tools
  ruleContent: glob pattern — Bash: command string, File: path, MCP: server__tool
  Uses preparePermissionMatcher() closure for efficient repeated matching
```

## AI Auto-Classifier (YOLO)

`yoloClassifier.ts` (1495 lines): fast paths skip classifier (safe-tool allowlist, read-only). Otherwise sends tool+input to small model → { safe, reason }. Denial tracking: consecutive + total counts, exceed limit → fall back to 'ask' user.

## Modes

`default` (prompt user), `acceptEdits` (auto-allow safe edits), `bypassPermissions` (allow all), `plan` (read-only), `auto` (AI classifier)

## Reading Order

1. `utils/permissions/permissions.ts` — main pipeline
2. `types/permissions.ts` — type definitions
3. `utils/permissions/filesystem.ts` — path-based checks
4. `utils/permissions/yoloClassifier.ts` — AI classifier
5. `utils/permissions/permissionSetup.ts` — rule loading

## Files

| File | Lines | What to read for |
|------|-------|------------------|
| `utils/permissions/permissions.ts` | 1486 | 10-step pipeline |
| `utils/permissions/permissionSetup.ts` | 1532 | Rule loading, Trust Dialog |
| `utils/permissions/yoloClassifier.ts` | 1495 | AI classifier |
| `utils/permissions/filesystem.ts` | 1777 | Path allowlist |
| `types/permissions.ts` | 441 | Type definitions |

## Neighbors

← `tools.md` (tool execution calls checkPermissions)
← `hooks.md` (PermissionRequest hooks override decisions)
→ `bootstrap.md` (permission mode in bootstrap state)
