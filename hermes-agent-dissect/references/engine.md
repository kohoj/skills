# Conversation Engine

## The Main Loop — 5 Stages

```
STAGE 1: PROMPT ASSEMBLY (AIAgent._build_system_prompt)
  Identity + skills manifest + context files (.hermes.md, AGENTS.md, .cursorrules)
  + Honcho memory guidance (if enabled) + tool use enforcement (model-specific)

STAGE 2: TOOL RESOLUTION (model_tools.get_tool_definitions)
  registry.get_definitions(enabled_toolsets) -> filter by check_fn()
  -> strip hallucination-inducing cross-references -> return OpenAI schemas

STAGE 3: LLM CALL (OpenAI / Anthropic SDK)
  _sanitize_api_messages() -> surrogate cleanup, budget warning stripping
  Anthropic: convert_messages_to_anthropic() + thinking/adaptive thinking
  OpenAI-compat: direct chat.completions.create(stream=True)

STAGE 4: TOOL EXECUTION (model_tools.handle_function_call)
  for each tool_call in response:
    _repair_tool_call() -> fix malformed JSON
    _deduplicate_tool_calls() -> remove identical duplicates
    _should_parallelize_tool_batch() -> safe-to-parallel check
      safe: read_file, search_files, web_search, vision_analyze, honcho_*
      never: clarify (interactive)
      path-scoped: read_file, write_file, patch (independent if non-overlapping)
    ThreadPoolExecutor(8) or sequential -> registry.dispatch()

STAGE 5: LOOP CONTROL
  No tool_calls -> done, return to user
  tool_calls -> append results, check iteration budget
  Context nearing limit -> ContextCompressor.compress()
  Honcho enabled -> sync observations post-turn
  Loop back to STAGE 3
```

## Key Abstractions

**AIAgent** (run_agent.py, 8551 lines): The core orchestrator. ~150+ methods handling session lifecycle, streaming, multi-provider integration, Honcho memory, tool deduplication, context compression triggers.

**IterationBudget**: Thread-safe counter. Parent shares budget pool, subagents get independent limits. `consume()` / `refund()` / `remaining` for turn tracking.

**HermesAgentLoop** (environments/agent_loop.py): Lighter reusable loop for RL environments. Same tool-calling pattern but without CLI, sessions, or Honcho. Returns AgentResult with messages, turns_used, reasoning_per_turn, tool_errors.

**Anthropic Adapter**: Full format translation layer. Handles OAuth/API key routing, thinking budget per effort level (xhigh→32K, low→4K), adaptive thinking for 4.6 models, beta headers, version detection.

**Reasoning Extraction**: Three provider formats: `message.reasoning_content` (standard), `message.reasoning` (some providers), `message.reasoning_details[].text` (OpenRouter style).

## Multi-Provider Architecture

```
AIAgent handles providers via credential_pool + anthropic_adapter:
  Anthropic (native) -> OAuth/API key, thinking, message conversion
  OpenRouter         -> OpenAI-compatible, extra_body for preferences
  OpenAI             -> Direct chat.completions
  Custom endpoints   -> Any OpenAI-compatible (VLLM, Ollama, etc.)
  Copilot ACP        -> via copilot_acp_client.py

Smart routing (optional): choose_cheap_model_route()
  If message ≤160 chars, ≤28 words, no code/URLs/complex keywords
  -> route to cheap model. Otherwise -> primary model.
```

## Reading Order

1. `run_agent.py` lines 447-600 — AIAgent.__init__, config surface
2. `run_agent.py` lines 170-212 — IterationBudget
3. `run_agent.py` lines 270-340 — parallelization safety checks
4. `model_tools.py` lines 368-443 — handle_function_call dispatcher
5. `model_tools.py` lines 35-125 — async/sync bridging
6. `agent/anthropic_adapter.py` lines 828-1000 — message conversion
7. `environments/agent_loop.py` lines 117-511 — RL agent loop
8. `agent/smart_model_routing.py` lines 66-111 — cheap model routing

## Files

| File | Lines | What to read for |
|------|-------|------------------|
| `run_agent.py` | 8551 | Core agent: loop, streaming, Honcho, sessions |
| `model_tools.py` | 473 | Tool dispatch, async bridge, discovery |
| `agent/anthropic_adapter.py` | 1321 | Anthropic format, OAuth, thinking |
| `environments/agent_loop.py` | 511 | Reusable multi-turn loop for RL |
| `agent/smart_model_routing.py` | 199 | Cheap vs strong model routing |
| `agent/auxiliary_client.py` | 1926 | Fallback vision model client |
| `agent/usage_pricing.py` | 656 | Token counting, cost estimation |

## Neighbors

← `bootstrap.md` (engine starts after config loaded)
→ `tools.md` (engine invokes tools via handle_function_call)
→ `context.md` (engine calls prompt assembly before each API call)
→ `memory.md` (Honcho sync happens post-turn)
→ `training.md` (HermesAgentLoop used by RL environments)
