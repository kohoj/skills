# Context Management: Prompt Assembly, Compression & Cache

## System Prompt — Layered Composition

```
Layer 1: DEFAULT_AGENT_IDENTITY       -> core Hermes Agent persona
Layer 2: Platform Hints               -> platform-specific instructions (CLI vs messaging)
Layer 3: Skills Index                  -> SOUL.md files from enabled skill directories
Layer 4: Context Files (scanned)      -> .hermes.md, AGENTS.md, .cursorrules, .claude.md
Layer 5: Memory Guidance              -> memory tool usage instructions (if memory enabled)
Layer 6: Session Search Guidance      -> history search capabilities
Layer 7: Tool Use Enforcement         -> extra prompting for models that need it
Always:  Honcho Turn Context          -> injected per-turn, NOT in history (ephemeral)
```

All assembly functions are stateless — no side effects, called fresh each turn.

## Context File Security

```
_scan_context_content(content, filename):
  Threat patterns scanned BEFORE injection:
    prompt_injection    -> "ignore instructions", "you are now"
    system_prompt_override -> role hijacking attempts
    exfil_curl         -> curl/wget with secrets
    read_secrets       -> env dumps, SSH key access
    invisible_chars    -> U+200B, U+FEFF zero-width markers

  Result: sanitized content or warning + truncation
```

## Context Compression

```
Triggers:
  prompt_tokens > threshold_percent * context_limit  -> auto-compress (~50%)
  should_compress_preflight() rough estimate          -> pre-API check

Pipeline:
  1. Prune old tool results (cheap pre-pass)
  2. Protect head messages (system + first N=3 exchanges)
  3. Protect tail messages (recent ~20K tokens, last N=20 messages)
  4. Summarize middle turns with auxiliary LLM:
     -> structured summary: Goal, Progress, Decisions, Files, Next Steps
  5. On subsequent compactions: update previous summary iteratively
  6. Replace compressed region with summary message

Budget controls:
  summary_target_ratio = 0.20 (20% of compressed content -> summary tokens)
  _SUMMARY_TOKENS_CEILING = 12K (prevents runaway summaries)
```

## Prompt Cache Strategy (Anthropic)

```
system_and_3 strategy (4 breakpoints):
  system prompt:     cache_control { type: 'ephemeral' }
  messages[-3]:      cache_control { type: 'ephemeral' }
  messages[-2]:      cache_control { type: 'ephemeral' }
  messages[-1]:      cache_control { type: 'ephemeral' }

  Content types handled: string, list of blocks, tool messages
  Result: ~75% input token cost reduction on multi-turn conversations

Stability tactic:
  Memory tool uses "frozen snapshot" pattern:
    System prompt loads memory at session start, never mutates
    Writes update disk immediately, but prompt unchanged
    -> prefix cache stays valid even as memory changes mid-session
```

## Token Estimation

```
Model metadata (agent/model_metadata.py):
  ~80 model family patterns with context lengths (128K, 64K, 32K, etc.)
  Provider prefix stripping: "openrouter/anthropic/claude-..." -> "claude-..."
  Endpoint probe cache: TTL 300s for external, 3600s for known models

  DEFAULT_FALLBACK_CONTEXT = 128K
  CONTEXT_PROBE_TIERS = [128K, 64K, 32K, 16K, 8K]
```

## Reading Order

1. `agent/prompt_builder.py` lines 134-275 — identity, guidance constants
2. `agent/prompt_builder.py` lines 36-127 — context file security scanning
3. `agent/prompt_builder.py` lines 664-815 — context file loading (.hermes.md, AGENTS.md)
4. `agent/context_compressor.py` lines 51-676 — ContextCompressor class
5. `agent/prompt_caching.py` — system_and_3 cache strategy (73 lines, read all)
6. `agent/model_metadata.py` lines 1-200 — provider prefixes, context tiers

## Files

| File | Lines | What to read for |
|------|-------|------------------|
| `agent/prompt_builder.py` | 816 | Prompt assembly, security scan, skills index |
| `agent/context_compressor.py` | 676 | Structured summarization, iterative updates |
| `agent/prompt_caching.py` | 73 | Anthropic cache breakpoint strategy |
| `agent/model_metadata.py` | 931 | Context lengths, provider detection |
| `agent/context_references.py` | 492 | Context file reference handling |
| `agent/redact.py` | 176 | Sensitive data redaction |

## Neighbors

← `engine.md` (engine calls prompt assembly before each API call)
→ `memory.md` (frozen snapshot pattern, Honcho ephemeral injection)
→ `skills.md` (skills index built during prompt assembly)
→ `tools.md` (tool schemas sorted for cache stability)
