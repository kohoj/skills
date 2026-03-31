# Extensions: MCP, Plugins, Skills, IDE Bridge & UI

## MCP Integration

```
Transports: stdio, sse, http, ws, sdk, claudeai-proxy
Config scopes (merge order): managed → user → project → local → dynamic → claudeai

Lifecycle:
  Load configs → connect (authenticate if needed) → list tools/resources/prompts
  → wrap as MCPTool (naming: mcp__{serverName}__{toolName})

Auth: OAuth 2.0 PKCE, XAA (enterprise), Keychain storage, auto-refresh
```

## Plugin System

```
Types: built-in (@builtin, enable/disable) + external (npm/GitHub install)
Manifest provides: skills, hooks, MCP servers, agent definitions, LSP servers
Scopes: user, project, local, managed (read-only)

Lifecycle: discover → validate → install → enable/disable → load at startup
  loadPluginCommands() → skills
  mcpPluginIntegration() → MCP servers
  loadPluginAgents() → agent definitions
```

## Skill System

```
Skill = prompt template + tool constraints + metadata

Sources:
  Bundled: skills/bundled/*.ts (compiled in binary)
  Plugin: from installed plugins
  Disk: ~/.claude/skills/*.md, .claude/skills/*.md (loadSkillsDir)
  MCP: from MCP server prompts

Execution (SkillTool.ts):
  Find skill → parse args → inject into template → fork agent
  → apply allowedTools restrictions → apply model override → query loop → return
```

## IDE Bridge

```
bridgeMain.ts (2999 lines) — IDE↔CLI communication
Transports: WebSocket (primary), SSE (fallback), CCR

Flow: IDE sends input/context → Bridge translates → CLI processes
  → results/permissions forwarded back → IDE renders inline
```

## Terminal UI (Ink Engine)

```
Render pipeline:
  React JSX → Custom Reconciler → Virtual DOM (DOMElement)
  → Yoga WASM Flexbox → Screen Buffer (2D grid)
  → Frame Diff → ANSI Patches → stdout

Performance:
  CharPool/StylePool: character/style interning (ASCII O(1))
  Blitting: unchanged layout → copy pixels from last frame
  DECSTBM: hardware terminal scrolling
  DEC 2026: synchronized output (atomic frames, zero flicker)
  Pool GC: reset every 5 min

Input:
  Raw stdin → parse-keypress (Kitty/xterm/Legacy protocols)
  → useInput() hook → PromptInput (multiline, history, autocomplete, Vim)

VirtualMessageList: only renders visible messages + buffer (1000s of messages OK)
```

## Reading Order

For MCP: `services/mcp/client.ts` lines 1-500 → `config.ts` → `auth.ts`
For plugins: `utils/plugins/pluginLoader.ts` lines 1-500 → `schemas.ts`
For skills: `skills/loadSkillsDir.ts` lines 1-400 → `tools/SkillTool/SkillTool.ts`
For bridge: `bridge/bridgeMain.ts` lines 1-500
For UI: `ink/ink.tsx` → `reconciler.ts` → `screen.ts` → `render-node-to-output.ts`

## Files

| File | Lines | What to read for |
|------|-------|------------------|
| `services/mcp/client.ts` | 3348 | MCP connection, tool listing |
| `services/mcp/config.ts` | 1578 | Multi-scope config |
| `services/mcp/auth.ts` | 2465 | OAuth/XAA auth |
| `utils/plugins/pluginLoader.ts` | 3302 | Plugin lifecycle |
| `utils/plugins/marketplaceManager.ts` | 2643 | Marketplace |
| `skills/loadSkillsDir.ts` | 1086 | Skill file parsing |
| `tools/SkillTool/SkillTool.ts` | 1108 | Skill execution |
| `bridge/bridgeMain.ts` | 2999 | IDE bridge |
| `ink/ink.tsx` | 1722 | Ink render loop |
| `ink/reconciler.ts` | 512 | React reconciler |
| `ink/screen.ts` | 1486 | Screen buffer, pools |
| `ink/render-node-to-output.ts` | 1462 | DOM → screen |
| `ink/parse-keypress.ts` | 801 | Keyboard protocols |
| `components/PromptInput/PromptInput.tsx` | 2338 | Input component |
| `components/VirtualMessageList.tsx` | 1081 | Virtual scroll |

## Neighbors

→ `tools.md` (MCP→MCPTool, skills→SkillTool)
→ `hooks.md` (plugins register hooks)
→ `agents.md` (plugins define agents)
← `bootstrap.md` (MCP started during init)
← `permissions.md` (MCP tools use same permission system)
