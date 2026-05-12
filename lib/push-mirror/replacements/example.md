# replacements/example.md

Per-target find-replace rules consumed by `anon.py`. Format: one rule per line as
`regex_pattern → replacement`.

Rename to `<target>.md` (e.g., `claude-configs.md`) and put real rules. Each public
target gets its own file. Files matching `replacements/*.md` (except `example.md`)
are typically gitignored — they contain mappings to the actual private names you
want to redact.

## Format rules

- Whitespace around `→` is required.
- Lines starting with `#` are comments.
- Empty lines are ignored.
- Patterns are Python regexes. Use `(?i)` prefix for case-insensitive.
- Replacements are literal strings — no backreferences yet.

## Example rules

```
# Personal paths
/Users/yourname/                → /Users/user/
\\Users\\yourname\\             → /Users/user/

# Names
Your Full Name                  → User
yourname\.surname               → user

# Private project codenames
private-project-a               → example-project
internal-codename               → product

# Numeric IDs (Asana, Notion, etc)
\b1234567\b                     → 0000001
\b89012345\b                    → 00000002
```

## How anon.py uses this

`anon.py` reads this file, builds a list of `(regex, replacement)` pairs, and applies
them in order to stdin → stdout. It does NOT enforce the master `forbidden.txt` deny
list — that check happens after, at the call site, to catch anything the rules missed.
