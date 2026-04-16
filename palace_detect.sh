#!/bin/bash
# Detect the MemPalace palace path for the current project.
# Reads --palace arg from .mcp.json walking up from CWD.
# Falls back to ~/.mempalace/palace (global default).

~/.mempalace/venv/bin/python3 - << 'EOF'
import json, sys
from pathlib import Path

cwd = Path.cwd()
for d in [cwd] + list(cwd.parents):
    mcp = d / ".mcp.json"
    if mcp.exists():
        try:
            data = json.loads(mcp.read_text())
            args = data.get("mcpServers", {}).get("mempalace", {}).get("args", [])
            if "--palace" in args:
                print(args[args.index("--palace") + 1])
                sys.exit(0)
        except Exception:
            pass

print(str(Path.home() / ".mempalace" / "palace"))
EOF
