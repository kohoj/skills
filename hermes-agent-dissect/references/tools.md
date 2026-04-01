# Tool System

## The ToolEntry Interface

```python
class ToolEntry:
    name: str                 # "terminal", "browser", etc.
    toolset: str              # Tool grouping
    schema: dict              # OpenAI-format tool schema
    handler: Callable         # Sync or async function
    check_fn: Callable        # Availability check (e.g., API key present)
    requires_env: List[str]   # Required env vars
    is_async: bool
    description: str
    emoji: str

# Handler signature:
def handler(arg1, arg2, **kwargs) -> str:
    return json.dumps({...})  # Always returns JSON string
```

## Tool Registration — Import-Time Singleton

```python
# Each tool module at top level:
from tools.registry import registry
registry.register(
    name="web_search", toolset="web",
    schema={...}, handler=web_search_fn,
    check_fn=lambda: bool(os.getenv("TAVILY_API_KEY")),
)

# Discovery (model_tools._discover_tools):
import tools  # __init__.py re-exports all -> triggers registration
# Result: registry has all tools, no circular imports
```

**Key principles**: registry imports NOTHING from tool files, tool files import only registry. No circular deps.

## Toolset Composition

```
Atomic:   web, terminal, vision, image_gen, browser, file, tts, moa, skills, ...
Scenario: debugging = terminal + web + file
Platform: hermes-cli = all core tools
          hermes-telegram = hermes-cli + send_message
          hermes-gateway = union of all messaging platforms

Composition via "includes" field:
  { "tools": [...], "includes": ["web", "terminal"] }

resolve_toolset(name, visited=set()):
  Recursively resolves includes, cycle-safe via visited set
  Special: "all" or "*" -> every registered tool
  Fallback: check plugin registry for dynamically-added toolsets
```

## Async/Sync Bridge (model_tools.py)

```
Problem: async tool handlers in sync contexts, "Event loop is closed" from cached clients

_get_tool_loop()     -> persistent event loop for main CLI thread
_get_worker_loop()   -> per-thread persistent loop (threading.local)
_run_async(coro)     -> smart dispatch:
  Running loop detected -> spawn thread with asyncio.run()
  Worker thread         -> use per-thread persistent loop
  Main thread           -> use shared persistent loop
```

## Execution Pipeline

```
1. Response arrives with tool_calls
2. _repair_tool_call() -> fix malformed JSON args
3. _deduplicate_tool_calls() -> remove identical duplicates
4. _should_parallelize_tool_batch() -> safety check
5. For each tool_call:
   a. handle_function_call(name, args, ...)
   b. Agent-loop tools intercepted: todo, memory, session_search, delegate_task
   c. Plugin hooks: pre_tool_call / post_tool_call
   d. registry.dispatch(name, args) -> handler() -> JSON result
6. Results appended to messages
```

## Tool Availability Gating

```
get_tool_definitions(enabled_toolsets, disabled_toolsets):
  1. resolve_toolset() -> flat tool list
  2. registry.get_definitions() -> filter by check_fn()
     (model never sees unavailable tools -> no hallucination)
  3. Dynamic schema modification:
     execute_code -> only list actually-available sandbox tools
  4. Strip cross-references from descriptions (prevents tool confusion)
```

## Reading Order

1. `tools/registry.py` — complete ToolEntry + ToolRegistry (read all, 275 lines)
2. `toolsets.py` lines 1-200 — TOOLSETS dict, composition pattern
3. `toolsets.py` lines 396-472 — resolve_toolset(), resolve_multiple_toolsets()
4. `model_tools.py` lines 35-125 — async bridge
5. `model_tools.py` lines 234-353 — get_tool_definitions()
6. `model_tools.py` lines 368-443 — handle_function_call()
7. `tools/__init__.py` — facade re-exports (shows full tool inventory)

## Files

| File | Lines | What to read for |
|------|-------|------------------|
| `tools/registry.py` | 275 | ToolEntry, ToolRegistry singleton |
| `toolsets.py` | 642 | Toolset definitions, composition, resolution |
| `model_tools.py` | 473 | Discovery, async bridge, dispatch |
| `tools/__init__.py` | 263 | Tool inventory, facade re-exports |
| `tools/approval.py` | 671 | Dangerous command approval system |
| `tools/file_tools.py` | 824 | File ops with read-size guard, device blocklist |
| `tools/code_execution_tool.py` | 814 | Sandboxed code execution |

## Neighbors

← `engine.md` (engine invokes tools via handle_function_call)
→ `terminals.md` (terminal_tool dispatches to backends)
→ `skills.md` (skills_tool manages skill lifecycle)
→ `integrations.md` (MCP tools, delegate_tool, plugin tools)
