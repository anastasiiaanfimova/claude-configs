# CLAUDE.md — TypeScript / Node project template

Drop this into the root of a TS/Node project and edit per your stack.
Claude Code auto-loads `CLAUDE.md` from the project root every session.

---

## Stack

- **Node version:** 20+ (pin in `.nvmrc` or `engines` in `package.json`)
- **Package manager:** `pnpm` (or `npm` — pick one and commit the matching lockfile)
- **Linter / formatter:** ESLint + Prettier (or `biome` for a unified tool)
- **Type checker:** `tsc --noEmit` in CI; strict mode on
- **Test runner:** `vitest` (preferred 2026) or `jest`
- **Test layout:** `*.test.ts` colocated with source, or `tests/` mirroring `src/`

## Conventions

- **TypeScript:** `strict: true` in `tsconfig.json`; no `any` without comment explaining why
- **Imports:** absolute paths via `tsconfig` `paths`; no deep relative `../../../`
- **Async:** `async/await` over raw promises; never floating promises (`@typescript-eslint/no-floating-promises`)
- **Errors:** typed error classes; avoid throwing strings; result types (`Result<T, E>`) for predictable failure paths
- **Logging:** structured logger (`pino`, `winston`) — never `console.log` in production code

## Commands

```bash
pnpm install                # install
pnpm run dev                # dev server
pnpm run build              # production build
pnpm run test               # run tests
pnpm run lint               # eslint
pnpm run format             # prettier
pnpm run typecheck          # tsc --noEmit
```

## Tests

- New behavior → new test first (TDD).
- `describe` blocks per module, `it` blocks per behavior.
- Use `vi.mock` (vitest) / `jest.mock` sparingly — prefer real implementations or fakes.
- API tests: `supertest` against the actual server.
- Frontend: `@testing-library/react` over Enzyme; query by role/text, not test-id.

## Project-specific notes

<!-- Add things like:
- which directories are generated and shouldn't be edited
- which scripts are off-limits without permission
- environment variable conventions (.env, dotenv-vault, Infisical?)
- monorepo structure if applicable (workspaces? turborepo? nx?)
- API client codegen workflow if applicable
-->

## What Claude should NOT do

- Don't `npm install` new deps without checking `package.json` first.
- Don't downgrade TypeScript / Node versions to make code "work".
- Don't suppress lints with `// eslint-disable-next-line` unless the rule clearly doesn't apply.
- Don't commit `dist/`, `node_modules/`, `.next/`, `coverage/`.
