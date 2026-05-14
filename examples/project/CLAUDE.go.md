# CLAUDE.md — Go project template

Drop this into the root of a Go project and edit per your stack.
Claude Code auto-loads `CLAUDE.md` from the project root every session.

---

## Stack

- **Go version:** 1.22+ (pin in `go.mod`)
- **Module layout:** `cmd/<binary>/main.go`, `internal/` for non-importable packages, `pkg/` for reusable
- **Linter:** `golangci-lint` (configure via `.golangci.yml`)
- **Test runner:** `go test ./...` + `testify` for assertions if preferred
- **Test layout:** `_test.go` files alongside the code they test (Go convention)

## Conventions

- **Error handling:** explicit `if err != nil`; wrap with `fmt.Errorf("...: %w", err)` for context
- **Naming:** exported = `CapitalCase`, unexported = `lowerCase`; short names in small scopes
- **Interfaces:** keep small (1-3 methods); declare at consumer, not provider
- **Concurrency:** `context.Context` first param on any function that does I/O or might block
- **Logging:** `log/slog` (stdlib structured logging, 1.21+) — no `fmt.Println` in production code

## Commands

```bash
go mod tidy                 # sync go.mod with imports
go test ./...               # run all tests
go test -race ./...         # detect data races
go build ./cmd/...          # build all binaries
golangci-lint run           # lint
go vet ./...                # vet
```

## Tests

- New behavior → new test first (TDD).
- Table-driven tests where there are multiple cases — `tests := []struct{...}{...}` then `t.Run(tt.name, func(t *testing.T) {...})`.
- Use `t.Helper()` in test helpers.
- Integration tests: build tag (`//go:build integration`) so they run separately.
- DB tests: real Postgres via `testcontainers-go`, not sqlmock.

## Project-specific notes

<!-- Add things like:
- which packages are off-limits without permission (e.g., vendored, generated proto/openapi clients)
- environment variable conventions (Viper? envconfig? plain os.Getenv?)
- generated code workflow (protoc-gen-go? sqlc?)
- secret handling (Vault? AWS Secrets Manager?)
-->

## What Claude should NOT do

- Don't add deps without checking `go.mod` — vendoring decisions matter.
- Don't silence `go vet` or `golangci-lint` findings without comment.
- Don't ignore `context.Context` deadline propagation in new code.
- Don't commit binaries, `vendor/` (unless project policy is to vendor), or `.idea/`.
