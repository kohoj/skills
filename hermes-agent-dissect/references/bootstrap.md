# Bootstrap, Configuration & Credentials

## Entry Points (4 modes)

```
Mode 1: CLI Interactive (cli.py)
  load_cli_config() -> deep merge config.yaml + env vars + project overrides
  prompt_toolkit REPL -> AIAgent.run_conversation() -> streaming display
  Slash commands: /new, /compress, /undo, /tools, /skills

Mode 2: CLI Single-Query (cli.py -q "...")
  Same config loading -> single AIAgent call -> stdout -> exit

Mode 3: Gateway Service (hermes_cli/main.py -> gateway)
  hermes gateway start -> GatewayRunner -> platform adapters -> persistent service

Mode 4: ACP Server (acp_adapter/__main__.py)
  hermes acp -> HermesACPAgent -> editor protocol -> tool discovery
```

## Configuration Layering

```
Priority (highest → lowest):
  1. Environment variables (ANTHROPIC_API_KEY, TERMINAL_ENV, etc.)
  2. ~/.hermes/config.yaml (primary user-facing)
  3. ~/.hermes/.env (dotenv secrets)
  4. ~/.hermes/gateway.json (legacy fallback)
  5. Built-in defaults (hermes_cli/config.py DEFAULT_CONFIG)

Profile support: --profile/-p flag pre-parsed before imports
  Sets HERMES_HOME to ~/.hermes/profiles/<name>/
  Entire config tree isolated per profile
```

**Key principles**: env vars override everything, profile isolation via HERMES_HOME, lazy module imports for fast CLI startup.

## Credential Pool — Multi-Provider Fallover

```python
PooledCredential:
  provider, auth_type (oauth | api_key), priority
  access_token, refresh_token, expires_at
  last_status, last_error_code, request_count

Strategies: FILL_FIRST | ROUND_ROBIN | RANDOM | LEAST_USED
  429 error -> 1 hour cooldown
  Other errors -> 24 hour cooldown

Seeding: env vars -> .env -> auth.json -> config.yaml -> custom providers
  custom: prefix for OpenAI-compatible endpoints ("custom:local_llm")
```

## Path Management (hermes_constants.py)

```
get_hermes_home()        -> HERMES_HOME env var or ~/.hermes
get_optional_skills_dir() -> ~/.hermes/skills/ (backward compat)
get_hermes_dir(new, old)  -> prefers existing old paths (migration-safe)

API endpoints:
  OPENROUTER_BASE_URL   = "https://openrouter.ai/api/v1"
  AI_GATEWAY_BASE_URL   = "https://ai-gateway.vercel.sh/v1"
  NOUS_API_BASE_URL     = "https://inference-api.nousresearch.com/v1"
```

## Reading Order

1. `cli.py` lines 85-443 — config loading, env var bridging
2. `hermes_cli/main.py` lines 1-200 — CLI dispatcher, profile override
3. `hermes_cli/config.py` lines 198-273 — DEFAULT_CONFIG structure
4. `agent/credential_pool.py` lines 85-150 — PooledCredential dataclass
5. `agent/credential_pool.py` lines 259-826 — CredentialPool strategies
6. `hermes_constants.py` — path management, reasoning config
7. `hermes_cli/setup.py` lines 1-200 — interactive setup wizard
8. `utils.py` — atomic file I/O (JSON/YAML)

## Files

| File | Lines | What to read for |
|------|-------|------------------|
| `cli.py` | 7952 | Config loading, TUI REPL, tool display |
| `hermes_cli/main.py` | 5046 | CLI dispatcher, profile support, session browser |
| `hermes_cli/config.py` | 2200 | Config management, defaults, secure permissions |
| `hermes_cli/setup.py` | 2860 | Interactive setup wizard |
| `hermes_cli/auth.py` | 2578 | Authentication flows |
| `agent/credential_pool.py` | 848 | Multi-credential fallover |
| `hermes_constants.py` | 106 | Paths, API URLs, reasoning config |
| `utils.py` | 108 | Atomic file I/O (temp+fsync+rename) |

## Neighbors

→ `engine.md` (after bootstrap, control flows to AIAgent loop)
→ `context.md` (config drives prompt assembly parameters)
→ `integrations.md` (ACP entry point, plugin discovery during init)
→ `gateway.md` (gateway mode starts platform adapters)
