# Contributing to System Design Arena

Thanks for considering a contribution — whether it's a bug report, a new persona, a test, or a docs fix, it's welcome here.

## Ways to contribute

- **Bug reports** — open an [issue](https://github.com/ashikvarma11/system-design-arena/issues) with steps to reproduce, what you expected, and what happened. Include your Python/Node versions and OS if it's environment-related.
- **Feature requests** — open an issue describing the use case, not just the implementation. Debate mechanics, new personas, and retrieval improvements are all in scope.
- **Good first issues** — backend and frontend test coverage is currently thin (`pytest` and Vitest are wired up but mostly untested). Adding tests for the orchestrator, `llm_client.py` fallback logic, or the debate-arena components is a great low-risk way to get familiar with the codebase.
- **Docs** — if something in the README confused you while setting up, that's a real bug in the docs. Fix it.

## Development setup

See [Getting Started](README.md#getting-started) in the README for the full local setup (Qdrant via Docker, backend venv + `.env`, frontend `npm install`). This file assumes you already have it running.

## Project conventions

**Backend** (`backend/app/`) follows a layered structure — keep new code in the matching layer rather than mixing concerns:

- `api/routes/` — thin FastAPI route handlers, no business logic.
- `services/` — business logic, called by routes.
- `orchestration/` — the debate loop and persona definitions.
- `retrieval/` — Qdrant access.
- `persistence/` — SQLAlchemy models and DB access.
- `ingestion/` — turning raw user input into a `ProblemBrief`.

**Frontend** (`frontend/src/app/`) uses Angular 22 standalone components and signals (no NgModules, no RxJS state where a signal will do). Structure:

- `core/` — services and models used app-wide.
- `features/` — one folder per route/screen (`problem-input/`, `debate-arena/`, `history/`).
- `shared/` — components reused across features.

Match the style of the file you're editing. There's no configured backend linter beyond what's implied by existing code; the frontend uses [Prettier](https://prettier.io/) (already a devDependency) — run it before committing:

```bash
cd frontend
npx prettier --write .
```

## Adding a new persona

The debate is the core extension point. Start with:

- [`backend/app/orchestration/personas.py`](backend/app/orchestration/personas.py) — persona constants and system prompts.
- [`backend/app/orchestration/orchestrator.py`](backend/app/orchestration/orchestrator.py) — the `run_debate()` loop that decides who speaks when, what they retrieve, and what gets persisted.

Keep the loop bounded and explicit — no open-ended "agent decides when it's done" behavior. If your persona needs retrieval, follow the existing dimension-agent pattern (query Qdrant with the current proposal text, filtered by a `dimension_hint`) rather than a one-off implementation.

## Commit style

Short, imperative, present-tense subject lines describing what changed, e.g.:

```
Add retry backoff to Qdrant client
Fix SSE stream not closing on client disconnect
```

Look at `git log` for more examples.

## Pull request process

1. Fork the repo and create a branch off `master` (`feature/your-thing` or `fix/your-thing`).
2. Make your changes, following the conventions above.
3. Test locally — run the app end-to-end (submit a problem, watch a debate stream, download a plan) for anything touching the debate loop or streaming, not just unit tests.
4. Open a PR describing **what** changed and **why**. Link any related issue.
5. Be responsive to review feedback — this is a small solo-maintained project, so response times may vary, but PRs are genuinely welcome.

## Reporting security issues

Don't commit `.env` files or real API keys — `.env` is already gitignored, keep it that way. If you find a security issue (e.g. a way to exhaust another user's provider quota, an injection vector in file upload/parsing), please open a GitHub issue with details; there's no dedicated security contact yet for a project this size.
