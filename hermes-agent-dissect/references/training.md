# RL Training & Environments

## Two-Phase Architecture

```
Phase 1: OpenAI-Compatible (standard tool_calls)
  HermesAgentLoop uses server.chat_completion()
  Model returns tool_calls natively
  Used for: OpenAI, Anthropic, OpenRouter

Phase 2: VLLM/SGLang (client-side tool parsing)
  Model generates raw text with <tool_call> tags
  Client-side parsers extract tool calls:
    deepseek_v3_parser, qwen3_coder_parser, glm45_parser, etc.
  Used for: self-hosted models via VLLM

Detection: _use_managed_server() checks environment
  Phase 2 if: VLLM/SGLang detected + tool_call_parser configured
```

## Atropos Base Environment

```python
class HermesAgentBaseEnv(BaseEnv):         # 671 lines
    # Subclasses must implement:
    async def setup()                      # Load dataset, init state
    def get_next_item() -> Item            # Next dataset item
    def format_prompt(item) -> str         # Convert to user message
    async def compute_reward(ctx) -> float # Score rollout via ToolContext
    async def evaluate()                   # Periodic evaluation

    # Built-in:
    collect_trajectory():
      1. _resolve_tools_for_group() -> sample toolsets from distribution
      2. Run HermesAgentLoop with messages + tools
      3. Build ToolContext (unrestricted tool access for verifier)
      4. compute_reward(ctx) -> score
      5. Return ScoredDataItem with messages/tokens/masks/scores

    # Toolset sampling:
    _resolve_tools_for_group():
      If distribution configured -> sample from toolset_distributions
      Else -> use explicit enabled_toolsets list
```

## HermesAgentLoop (Multi-Turn Engine)

```
environments/agent_loop.py (511 lines)

AgentResult:
  messages, managed_state, turns_used
  finished_naturally, reasoning_per_turn, tool_errors

Loop:
  for turn in range(max_turns):
    response = await server.chat_completion(messages, tools, ...)
    tool_calls = response.choices[0].message.tool_calls
    if not tool_calls: break  # finished naturally
    for tc in tool_calls:
      result = await handle_function_call(tc.name, tc.args)
      messages.append({"role": "tool", "content": result})

Thread pool: ThreadPoolExecutor(max_workers=128)
  Resizable via resize_tool_pool() for concurrent eval tasks

Reasoning extraction (3 formats):
  message.reasoning_content       # standard
  message.reasoning               # some providers
  message.reasoning_details[].text # OpenRouter style
```

## ToolContext — Unrestricted Verifier Access

```python
class ToolContext:                         # 475 lines
    terminal(command) -> {exit_code, output}
    read_file(path), write_file(path, content)
    upload_file(local, remote)             # base64 chunked, 60KB chunks
    download_file(remote, local)
    web_search(query), web_extract(url)
    browser_navigate(url), browser_snapshot()
    call_tool(name, **args)                # call ANY registered tool
    cleanup()                              # release VMs, browsers, processes

    # Thread-safe async wrapper:
    _run_tool_in_thread() with 300s timeout per call
    Same task_id scopes tools to rollout's sandbox
```

## Agentic OPD Environment (On-Policy Distillation)

```
environments/agentic_opd_env.py

Innovation: extract hints from next-state signals via LLM judge
  After agent acts -> observe terminal output / test results
  Judge LLM: "is this helpful? extract hint if so"
  Majority voting: 3 independent judge queries per (turn, next_state)
  Dense training signal: teacher logprobs per token position

AgenticOPDConfig:
  opd_enabled=True, distill_topk=50, prm_votes=3
  correctness_weight=0.7, efficiency_weight=0.15, tool_usage_weight=0.15

Fallback: 8 built-in coding tasks (fizzbuzz, palindrome, two_sum, etc.)
```

## Batch Runner — Parallel Processing

```
batch_runner.py (1285 lines)

Pipeline:
  1. Load JSONL dataset (prompts)
  2. Split into batch_size chunks
  3. Process batches in parallel (multiprocessing.Pool)
  4. Per-prompt: sample toolsets, run agent, extract stats
  5. Checkpoint after each batch (content-based resume)
  6. Combine into trajectories.jsonl

Resume: content-based matching (by prompt text, not index)
  Handles dataset reordering gracefully

Stats collected:
  Tool usage (success/failure per tool)
  Reasoning coverage (turns with/without reasoning)
  Filter: discard zero-reasoning samples
```

## Trajectory Compression

```
trajectory_compressor.py (1519 lines)

Algorithm:
  1. Count tokens per turn (Kimi-K2-Thinking tokenizer)
  2. If under target (15250 tokens): skip
  3. Find compressible region (between protected head/tail)
  4. Calculate tokens to save
  5. Summarize compressed turns with LLM (Gemini Flash)
  6. Replace with summary message
  7. Keep remaining turns intact

Protected turns: first system/human/gpt/tool, last N=4
Parallel processing: async with semaphore rate limiting
Per-trajectory timeout: 300s (prevents runaway summarization)
```

## Reading Order

1. `environments/hermes_base_env.py` lines 180-600 — HermesAgentBaseEnv
2. `environments/agent_loop.py` lines 117-511 — HermesAgentLoop
3. `environments/tool_context.py` lines 67-475 — ToolContext
4. `environments/agentic_opd_env.py` lines 318-400 — OPD config + env
5. `batch_runner.py` lines 512-1104 — BatchRunner class
6. `trajectory_compressor.py` lines 304-775 — TrajectoryCompressor
7. `toolset_distributions.py` — probabilistic toolset sampling (200 lines)

## Files

| File | Lines | What to read for |
|------|-------|------------------|
| `environments/hermes_base_env.py` | 671 | Abstract RL base, toolset sampling |
| `environments/agent_loop.py` | 511 | Multi-turn loop, reasoning extraction |
| `environments/tool_context.py` | 475 | Unrestricted verifier tool access |
| `environments/agentic_opd_env.py` | 1213 | On-policy distillation, hint extraction |
| `environments/web_research_env.py` | 718 | Multi-hop web research tasks |
| `batch_runner.py` | 1285 | Parallel batch processing, checkpointing |
| `trajectory_compressor.py` | 1519 | Token-budget trajectory compression |
| `toolset_distributions.py` | 200 | Probabilistic toolset sampling for RL |

## Neighbors

← `engine.md` (HermesAgentLoop is the RL version of AIAgent loop)
← `tools.md` (ToolContext dispatches to tool registry)
← `terminals.md` (RL envs configure terminal backend per experiment)
→ `memory.md` (checkpoints used for RL rollback)
