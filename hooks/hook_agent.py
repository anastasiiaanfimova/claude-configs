#!/usr/bin/env python3
"""
Wrapper for mempalace hooks that injects agent name into block reasons.

Usage (in Claude Code settings hooks):
  Stop:        MEMPALACE_AGENT=claw cat | python3 ~/.mempalace/hook_agent.py stop
  StopFailure: MEMPALACE_AGENT=claw cat | python3 ~/.mempalace/hook_agent.py stopfailure
  PreCompact:  MEMPALACE_AGENT=claw cat | python3 ~/.mempalace/hook_agent.py precompact

Reads MEMPALACE_AGENT from env (falls back to 'claude').
Passes stdin to mempalace hook, then appends the agent name to any block reason
so Claude knows which diary wing to write to.

For precompact: always allows so compaction can proceed.
For stopfailure: reuses stop hook but prepends crash notice to the block reason.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

hook = sys.argv[1] if len(sys.argv) > 1 else "stop"
agent = os.environ.get("MEMPALACE_AGENT", "claude")

data = sys.stdin.buffer.read()

# For precompact: check if we already blocked once this session
# If yes, allow compaction to proceed (infinite-loop prevention)
if hook == "precompact":
    print(json.dumps({}))
    sys.exit(0)

# stopfailure: reuse stop hook but flag the crash in the reason
crash_prefix = "[SESSION CRASHED — API error] " if hook == "stopfailure" else ""
mempalace_hook = "stop" if hook == "stopfailure" else hook

result = subprocess.run(
    [sys.executable, "-m", "mempalace", "hook", "run", "--hook", mempalace_hook, "--harness", "claude-code"],
    input=data,
    capture_output=True,
)

try:
    out = json.loads(result.stdout or b"{}")
except (json.JSONDecodeError, ValueError):
    out = {}

if "reason" in out:
    out["reason"] = f'mempalace (agent="{agent}"): {crash_prefix}{out["reason"]}'
elif crash_prefix:
    out["reason"] = f'mempalace (agent="{agent}"): {crash_prefix}Write a brief diary entry noting the session ended with an API error, then let the session end.'

print(json.dumps(out))
