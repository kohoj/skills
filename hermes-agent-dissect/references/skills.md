# Skills System

## SOUL.md Format — Skill Interface

```markdown
---
name: "Skill Name"
description: "What it does"
conditions:
  - requires: "ENVIRONMENT_VARIABLE"
  - requires_model: "claude-*"
  - platform: "terminal"  # or "web", "any"
  - tags: ["web_dev", "python"]
---

## Instructions
Skill content here — injected into system prompt or loaded on demand.
```

## Progressive Disclosure (3 tiers)

```
Tier 1: skills_list() -> metadata only (~1KB)
  Name, description, tags, readiness status
  Token-efficient: caps returned size to avoid prompt bloat

Tier 2: skill_view() -> full content
  Load SKILL.md, parse frontmatter, check setup requirements
  SkillReadinessStatus: Available | Setup_Needed | Unsupported

Tier 3: skill_view() with linked files
  Follow file references in skill content
  Load supporting files (examples, schemas, etc.)
```

## Skills Discovery

```
Sources:
  ~/.hermes/skills/         -> user-installed skills
  ./.hermes/skills/         -> project-local skills
  External dirs (config)    -> configurable extra skill locations
  Built-in (bundled)        -> compiled into binary

Build index (prompt_builder.build_skills_system_prompt):
  Walk skill directories -> parse frontmatter
  Filter by platform/OS -> filter by disabled list
  Generate skills manifest for system prompt
  Cache via _load_skills_snapshot() / _write_skills_snapshot()
```

## Slash Command Integration

```
scan_skill_commands():
  Walk ~/.hermes/skills/ -> match /dirname to /command
  /plan -> build_plan_path() -> .hermes/plans/ default

build_skill_invocation_message():
  Load skill content -> format as user message
  Include activation note + setup warnings + supporting files

build_preloaded_skills_prompt():
  Load multiple skills at session startup
  Inject into system prompt (not as tool calls)
```

## Skills Hub — Lifecycle Management

```
do_search()  -> search registries, Rich table display
do_browse()  -> paginated browse, official-first, dedup by trust level
do_install() -> fetch -> quarantine -> scan -> confirm -> install
  Auto-detect category for official skills
  Invalidate prompt cache on install
do_inspect() -> preview without installing (first 50 lines)
do_update()  -> upstream diff detection
do_publish() -> validate -> self-scan -> fork repo -> PR to GitHub
do_tap()     -> manage custom registry sources
do_snapshot_export/import() -> portable config transfer
```

## Security Scanning (skills_guard.py)

```
Threat patterns:
  Exfiltration: curl/wget with secrets, env dumps, SSH key access, DNS exfil
  Prompt injection: "ignore instructions", role hijacking, deception
  Destructive: rm -rf, mkfs, kill -9, fork bombs
  Persistence: authorized_keys, rc file modification

Trust-aware policy:
  builtin -> always trusted (no scan)
  community -> scan required, verdict: safe | caution | dangerous

Atomic write with rollback:
  Write to temp -> scan -> if dangerous: restore original
  Prevents malicious content from persisting even briefly
```

## Skill Manager Tool

```
skill_manage() dispatcher:
  create -> directory + SKILL.md + security scan
  edit   -> full rewrite + rollback on scan failure
  patch  -> targeted find-and-replace
  delete -> removal + empty parent cleanup
  write_file/remove_file -> supporting file management

Validation: frontmatter syntax, name/category constraints
Path traversal: normalize + resolve all file paths
```

## Reading Order

1. `tools/skills_tool.py` lines 109-752 — SkillReadinessStatus, skills_list()
2. `tools/skills_tool.py` lines 755-1226 — skill_view() full loading
3. `agent/prompt_builder.py` lines 291-651 — build_skills_system_prompt()
4. `agent/skill_commands.py` — slash command parsing (298 lines, read all)
5. `tools/skills_guard.py` lines 56-200 — threat patterns, ScanResult
6. `tools/skill_manager_tool.py` lines 262-586 — CRUD operations
7. `hermes_cli/skills_hub.py` lines 307-875 — install/publish workflows

## Files

| File | Lines | What to read for |
|------|-------|------------------|
| `tools/skills_tool.py` | 1345 | Progressive disclosure, readiness checks |
| `tools/skill_manager_tool.py` | 702 | CRUD, atomic writes, rollback |
| `tools/skills_hub.py` | 2691 | Registry adapters, GitHub auth |
| `tools/skills_guard.py` | 1105 | Security scanning, threat patterns |
| `agent/prompt_builder.py` | 816 | Skills index in system prompt |
| `agent/skill_commands.py` | 298 | Slash command parsing |
| `agent/skill_utils.py` | 271 | Frontmatter parsing, platform filtering |
| `hermes_cli/skills_hub.py` | 1220 | Hub CLI commands, install/publish |
| `hermes_cli/skills_config.py` | 187 | Skills configuration |

## Neighbors

← `context.md` (skills index built during prompt assembly)
→ `tools.md` (skills_tool registered in tool registry)
→ `integrations.md` (skills can provide MCP servers, hooks)
← `gateway.md` (platform-filtered skills per adapter)
