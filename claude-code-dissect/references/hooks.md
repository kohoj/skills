# Hooks System

## Event Types

```
Session:     SessionStart, SessionEnd (1.5s timeout!), Setup
Tool:        PreToolUse, PostToolUse, PostToolUseFailure
Permission:  PermissionRequest (can approve/deny/modify!), PermissionDenied
Agent:       SubagentStart, SubagentStop
Other:       FileWatch, ConfigChange, Notification
```

## Definition (settings.json)

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": { "toolName": "Bash", "ruleContent": "npm *" },
      "command": "echo '{\"decision\": \"allow\"}'",
      "timeout": 10000
    }]
  }
}
```

## Execution Flow

```
1. Find matching hooks: filter by event → match toolName → match ruleContent (glob)
2. Prepare input: HOOK_EVENT_DATA env var (JSON with tool_name, tool_input, session_id)
3. Execute: spawn shell, capture stdout as JSON, timeout 10min (1.5s for SessionEnd)
4. Process output:
   PreToolUse:        { decision: "allow"|"deny", modifiedInput?: {...} }
   PermissionRequest: { decision: "approve"|"deny", updatedInput?: {...} }
   PostToolUse:       informational only
```

PermissionRequest hooks are the most powerful — they can auto-approve AND modify tool input before execution.

Matching: toolName (exact/alias/MCP pattern) AND ruleContent (glob). No matcher = match all.
Trust: ALL hooks require workspace trust dialog acceptance. Without trust: silently skipped.
Plugin hooks: same schema, applied alongside CLI hooks, can influence tool execution.

## Reading Order

1. `utils/hooks.ts` — complete engine (start with types at top)
2. `services/tools/toolHooks.ts` — tool lifecycle integration
3. `utils/hooks/sessionHooks.ts` — session lifecycle
4. `utils/hooks/hooksConfigManager.ts` — settings.json loading

## Files

| File | Lines | What to read for |
|------|-------|------------------|
| `utils/hooks.ts` | 5022 | Full engine: definition, matching, execution |
| `services/tools/toolHooks.ts` | 650 | Tool lifecycle integration |
| `utils/hooks/sessionHooks.ts` | 447 | Session hooks |
| `utils/hooks/hooksConfigManager.ts` | 400 | Settings loading |

## Neighbors

← `tools.md` (tool execution triggers hooks)
← `permissions.md` (PermissionRequest hooks override decisions)
← `extensions.md` (plugins register hooks)
