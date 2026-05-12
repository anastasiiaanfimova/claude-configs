#!/usr/bin/env python3
"""Anonymize stdin → stdout using a target's replacement rules.

Usage:
    anon.py <target>            # reads replacements/<target>.md
    anon.py --file <path>       # reads explicit file

The replacements file format is one rule per line:

    regex_pattern → replacement

Lines starting with `#` and empty lines are ignored. Patterns are Python
regular expressions; case-insensitive matches use the inline `(?i)` flag at
the start of the pattern.

This script ONLY substitutes — it does not enforce the master forbidden list.
The post-anonymization sanity scan against forbidden.txt happens in
push-mirror.sh after files are copied into the repo working tree.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

LIB_DIR = Path(__file__).resolve().parent
SEPARATOR = "→"


def load_rules(path: Path) -> list[tuple[str, str]]:
    rules: list[tuple[str, str]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if SEPARATOR not in line:
            continue
        pat, _, rep = line.partition(SEPARATOR)
        pat = pat.strip()
        rep = rep.strip()
        if not pat:
            continue
        rules.append((pat, rep))
    return rules


def resolve_target(target: str | None, file_arg: str | None) -> Path:
    if file_arg:
        return Path(file_arg).expanduser().resolve()
    if not target:
        sys.exit("anon.py: must pass <target> or --file")
    candidate = LIB_DIR / "replacements" / f"{target}.md"
    if not candidate.is_file():
        sys.exit(f"anon.py: replacements file not found: {candidate}")
    return candidate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", help="target name (e.g. qa-playbook)")
    parser.add_argument("--file", dest="file", help="explicit replacements file")
    args = parser.parse_args()

    rules_path = resolve_target(args.target, args.file)
    rules = load_rules(rules_path)

    text = sys.stdin.read()
    for pat, rep in rules:
        try:
            text = re.sub(pat, rep, text)
        except re.error as exc:
            sys.exit(f"anon.py: invalid regex {pat!r} in {rules_path}: {exc}")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
