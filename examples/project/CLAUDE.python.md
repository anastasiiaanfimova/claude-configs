# CLAUDE.md — Python project template

Drop this into the root of a Python project and edit per your stack.
Claude Code auto-loads `CLAUDE.md` from the project root every session.

---

## Stack

- **Python version:** 3.12+ (pin in `pyproject.toml`)
- **Package manager:** `uv` (fast, replaces pip/poetry/pyenv for most flows)
- **Linter / formatter:** `ruff` (replaces flake8+isort+black)
- **Type checker:** `mypy` or `pyright`
- **Test runner:** `pytest` + `pytest-asyncio` for async code
- **Test layout:** `tests/` mirroring the package structure

## Conventions

- **Imports:** standard library → third-party → local, blank line between groups
- **Type hints:** required on all public functions; `from __future__ import annotations` at the top of every module
- **Async:** `async def` for I/O, `def` for pure logic
- **Errors:** raise specific exception classes; never bare `except:`
- **Logging:** `logging.getLogger(__name__)` at module level; structured logs over f-strings in production

## Commands

```bash
uv sync                     # install dependencies from pyproject.toml + uv.lock
uv run pytest               # run tests
uv run ruff check .         # lint
uv run ruff format .        # format
uv run mypy <package>       # type-check
```

## Tests

- New behavior → new test first (TDD).
- One assertion per test where possible — clear failure messages.
- Use `pytest.fixture` for setup, not `setUp` (we're not using unittest).
- Async tests: `@pytest.mark.asyncio` decorator.
- DB tests: use `testcontainers` for real Postgres, not mocks.

## Project-specific notes

<!-- Add things like:
- which directories are off-limits (vendored code, generated)
- which scripts should NOT be touched without explicit permission
- which APIs are external vs internal
- environment variable conventions
- secret handling (Infisical? .env? vault?)
-->

## What Claude should NOT do

- Don't add new dependencies without checking `pyproject.toml` first — bloat is real.
- Don't change formatter/linter config silently; surface the change in the response.
- Don't suppress mypy/ruff errors with `# type: ignore` / `# noqa` unless the underlying issue is documented as out-of-scope.
- Don't commit `*.pyc`, `__pycache__/`, `.venv/`, `.pytest_cache/`.
