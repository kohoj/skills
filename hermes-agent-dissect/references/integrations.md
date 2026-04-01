# Integrations: ACP, MCP, Plugins & Delegation

## ACP Adapter (Agent Client Protocol)

```
acp_adapter/ — wraps Hermes AIAgent as editor-protocol service

HermesACPAgent (server.py):
  initialize()   -> protocol version, capabilities (session fork/list)
  new_session()   -> fresh AIAgent + unique session ID
  load_session()  -> restore persisted session from cwd
  resume_session() -> resume or create if not found
  cancel()        -> interrupt running agent
  fork_session()  -> deep-copy history to new session

SessionManager (session.py):
  Manages SessionState: session_id, agent, cwd, model, history
  create -> UUID + fresh AIAgent + register cwd
  fork -> deep-copy original history to new session
  list -> in-memory + persisted from DB

Content extraction:
  _extract_text() handles: TextContentBlock, ImageContentBlock,
  AudioContentBlock, ResourceContentBlock, EmbeddedResourceContentBlock

Thread pool: max_workers=4 for parallel agent execution
```

## MCP Integration (Model Context Protocol)

```
tools/mcp_tool.py (2019 lines)

Transports: stdio, HTTP
Auto-reconnection with exponential backoff
Thread-safe: dedicated event loop

Tool wrapping:
  MCP tool -> registered as hermes tool with mcp_ prefix
  Dynamic tool discovery via notifications
  Server-initiated sampling/createMessage supported

Security:
  _build_safe_env() -> filter Hermes secrets from subprocesses
  _sanitize_error() -> strip credentials before LLM sees errors
  _resolve_stdio_command() -> resolve npx/npm/node from multiple locations

CLI (hermes_cli/mcp_config.py, 646 lines):
  cmd_mcp_add()       -> discovery-first tool selection (interactive checklist)
  cmd_mcp_test()      -> test connection, show transport/auth/tools
  cmd_mcp_configure() -> reconfigure enabled tools per server

Auth: OAuth + header with env var interpolation
```

## Plugin System

```
hermes_cli/plugins.py (560 lines)

PluginManifest:
  name, version, description, author
  requires_env, provides_tools, provides_hooks
  source, path

Valid hooks:
  pre_tool_call, post_tool_call
  pre_llm_call, post_llm_call
  on_session_start, on_session_end

PluginContext (facade passed to plugins.register()):
  register_tool()   -> add tool to global registry
  inject_message()  -> send message into active conversation
  register_hook()   -> register lifecycle callback

Discovery (3 sources):
  ~/.hermes/plugins/        -> user-installed
  ./.hermes/plugins/        -> project-local
  pip entry-points          -> importlib.metadata

Lifecycle:
  discover -> validate manifest -> import module -> call register(ctx)
  invoke_hook() -> call all callbacks for hook_name (exception-safe per callback)
```

## Delegation (Subagent Architecture)

```
tools/delegate_tool.py (795 lines)

_build_child_agent():
  Fresh conversation, restricted toolset, own terminal session
  Blocked tools: delegation, clarify, memory, send_message, execute_code
  Credential override: subagents can route to different provider:model
  Depth limit: MAX_DEPTH=2 (no grandchildren)

Modes:
  Single task -> _run_single_child() in thread
  Batch (up to 3) -> parallel execution with per-task progress

Progress:
  Child tool calls relayed to parent display (spinner/gateway)
  Parent sees summarized result when child completes

Isolation:
  Fresh AIAgent instance
  No shared state with parent
  Own iteration budget (independent of parent)
```

## Mixture of Agents (MoA)

```
tools/mixture_of_agents_tool.py (562 lines)

Pattern: route query to multiple models, synthesize best answer
  Models queried in parallel
  Results ranked/combined
  Final answer from strongest model

Use case: complex queries benefiting from diverse perspectives
```

## Reading Order

1. `acp_adapter/server.py` lines 81-200 — HermesACPAgent
2. `acp_adapter/session.py` lines 58-200 — SessionManager
3. `tools/mcp_tool.py` lines 1-300 — MCP transport, security, wrapping
4. `hermes_cli/mcp_config.py` lines 173-500 — MCP add/test/configure
5. `hermes_cli/plugins.py` lines 86-482 — PluginManifest, PluginManager
6. `tools/delegate_tool.py` lines 150-567 — child agent building, execution
7. `tools/mixture_of_agents_tool.py` lines 1-200 — MoA routing pattern

## Files

| File | Lines | What to read for |
|------|-------|------------------|
| `acp_adapter/server.py` | 535 | ACP protocol server, capabilities |
| `acp_adapter/session.py` | 461 | Session lifecycle, fork |
| `acp_adapter/tools.py` | 215 | Tool discovery for editor |
| `acp_adapter/events.py` | 171 | Event streaming |
| `tools/mcp_tool.py` | 2019 | MCP transport, tool wrapping, security |
| `hermes_cli/mcp_config.py` | 646 | MCP CLI commands |
| `hermes_cli/plugins.py` | 560 | Plugin discovery, lifecycle, hooks |
| `tools/delegate_tool.py` | 795 | Subagent isolation, batch mode |
| `tools/mixture_of_agents_tool.py` | 562 | Multi-model routing |
| `tools/send_message_tool.py` | 906 | Cross-platform messaging |

## Neighbors

← `tools.md` (MCP/plugin tools registered in registry)
← `bootstrap.md` (ACP entry point, plugin init during startup)
← `engine.md` (delegate_tool creates child AIAgent instances)
→ `gateway.md` (send_message_tool uses platform adapters)
→ `skills.md` (plugins can provide skills)
