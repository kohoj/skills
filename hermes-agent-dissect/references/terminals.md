# Terminal Backends & Execution

## Backend Abstraction

```python
class BaseEnvironment:                     # tools/environments/base.py, 100 lines
    async def execute(command, timeout) -> {"output": str, "returncode": int}
    async def cleanup()
    def _prepare_command(command)           # sudo transformation
    def _build_run_kwargs()                 # standard subprocess.run params

Backends:
  local        -> direct execution, persistent shell
  docker       -> container with security hardening
  modal        -> serverless compute (Modal.com)
  daytona      -> sandbox isolation
  ssh          -> remote execution
  singularity  -> HPC container runtime
```

## Local Backend (tools/environments/local.py)

```
Persistent shell: reuse bash process for command sequence
  Unique markers (fences) isolate command output
  Provider env blocking: filter Hermes-managed secrets from subprocesses
  Interrupt support: check is_interrupted() during execution
  Git Bash on Windows: shutil.which + PATH search

Output fencing pattern:
  echo "===HERMES_FENCE_abc123===" -> command -> echo "===HERMES_FENCE_abc123==="
  Parse output between fences -> clean result
```

## Docker Backend (tools/environments/docker.py)

```
Security hardening:
  --cap-drop ALL                  # no Linux capabilities
  --security-opt no-new-privileges
  --pids-limit                    # prevent fork bombs
  Tmpfs mounts with noexec,nosuid,nodev

Resource limits: CPU, memory, disk (configurable)
Credential forwarding: selective env var passing via docker_forward_env
Docker discovery: check PATH + macOS app bundle locations (/Applications/Docker.app)
```

## Terminal Tool (tools/terminal_tool.py)

```
Main dispatcher:
  1. Select backend from config (terminal.env_type)
  2. Check disk usage warnings
  3. Check dangerous command patterns (30+ patterns)
  4. If dangerous: approval flow (manual, smart, or off)
  5. Execute via selected backend
  6. Return output + returncode

Process management:
  Background tasks: lifecycle management via process_registry
  Cleanup: terminal sessions + browser sessions on exit
  Timeout: per-command override or config default (180s)
```

## Dangerous Command Approval (tools/approval.py)

```
Patterns (30+):
  recursive rm, fork bombs, SQL drops, kill -9
  format/mkfs, shutdown/reboot, chmod 777
  SSH key manipulation, passwd changes

Approval modes:
  manual -> prompt user for yes/no
  smart  -> auxiliary LLM assesses real risk before prompting
  off    -> skip all approvals

Per-session state: thread-safe dict with pattern keys
Permanent allowlist: persisted to config.yaml
Combined guards: tirith (security scanning) + dangerous-command in single flow
```

## Persistent Shell Pattern

```
tools/environments/persistent_shell.py (277 lines)

Design:
  Single bash process per session (subprocess.Popen)
  stdin/stdout/stderr pipes maintained
  Command isolation via unique fence markers

Lifecycle:
  _start_shell() -> spawn bash with clean env
  execute() -> write command, read until fence
  cleanup() -> SIGTERM, wait, SIGKILL if needed

Benefits:
  Environment state preserved (cd, export, aliases)
  Faster than spawning new process per command
  Shell history accessible across commands

Tradeoffs:
  More complex output parsing (fence detection)
  Hung shell risk (need timeout handling)
  State leaks between commands (by design)
```

## Reading Order

1. `tools/environments/base.py` — abstract interface (100 lines, read all)
2. `tools/environments/local.py` lines 1-200 — persistent shell, env blocking
3. `tools/environments/docker.py` lines 1-200 — security hardening, resource limits
4. `tools/terminal_tool.py` lines 1-300 — dispatcher, disk usage, sudo
5. `tools/approval.py` lines 126-490 — danger detection, approval orchestration
6. `tools/environments/persistent_shell.py` — fence-based isolation (277 lines)
7. `tools/process_registry.py` lines 1-200 — background task lifecycle

## Files

| File | Lines | What to read for |
|------|-------|------------------|
| `tools/terminal_tool.py` | 1358 | Main dispatcher, sudo, disk usage |
| `tools/approval.py` | 671 | Dangerous command patterns, approval modes |
| `tools/process_registry.py` | 889 | Background task tracking |
| `tools/environments/base.py` | 100 | Abstract backend interface |
| `tools/environments/local.py` | 486 | Local execution, persistent shell |
| `tools/environments/docker.py` | 535 | Container security, resource limits |
| `tools/environments/modal.py` | 372 | Serverless execution |
| `tools/environments/ssh.py` | 307 | Remote SSH backend |
| `tools/environments/daytona.py` | 299 | Sandbox isolation |
| `tools/environments/singularity.py` | 391 | HPC container runtime |
| `tools/environments/persistent_shell.py` | 277 | Fence-based session reuse |

## Neighbors

← `tools.md` (terminal_tool registered in tool registry)
→ `engine.md` (tool execution dispatches to terminal backend)
→ `training.md` (RL environments configure backend per env)
→ `gateway.md` (gateway sessions use terminal tool)
