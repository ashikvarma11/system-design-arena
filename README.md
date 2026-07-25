# System Design Arena

Submit a system design prompt (free text or an uploaded architecture-decision file) and
watch six LLM personas debate it across constraints, performance, security, and feedback
dimensions — one agent explicitly critiquing another — converging on an agreed plan you can
download as Markdown.

Entire stack runs on free tiers only: no paid API keys, no required credit card, anywhere.

## Why this project

Most "AI engineer" portfolio projects are a RAG chatbot wrapped around a PDF. This is
deliberately not that. It demonstrates:

- **Multi-agent orchestration** — a bounded, hand-rolled debate loop (no LangGraph/CrewAI)
  where personas have distinct system prompts, react to each other's output, and one agent's
  entire job is to explicitly name and rebut a specific prior turn.
- **Streaming** — Server-Sent Events from FastAPI, consumed in Angular via `fetch` +
  `ReadableStream` (not `EventSource`, for full control over parsing and teardown).
- **A vector DB used for two different jobs**, not just "chat with your docs":
  1. A curated concept knowledge base (76 short notes on CAP theorem, sharding, OWASP
     categories, etc.) that agents retrieve from *before* arguing — retrieval feeds an
     argument, it isn't the final answer.
  2. Every debate turn ever produced is embedded on write, enabling cross-session recall:
     a completed debate surfaces similar past debates and the specific turn that matched.

## How it works

1. **Submit a problem** — free text or a `.txt`/`.md`/`.pdf` file describing a system design
   problem (e.g. "Design a URL shortener for 1M reads/sec, budget under $500/month").
2. **Brief normalization** — an LLM call structures the raw input into a `ProblemBrief`
   (`goals`, `constraints`, `non_goals`) before any debate starts.
3. **Bounded debate** (2-5 rounds, user-selectable) — a fixed `for` loop, never open-ended:
   - **Proposer/Architect** kicks off with an initial architecture.
   - **Constraints**, **Performance**, and **Security** agents each react to the current
     proposal, retrieving 2-3 grounding notes from the concept KB first.
   - **Critic** rebuts exactly one specific prior turn — it must quote and name what it's
     attacking (`critiques_turn_id` is the load-bearing field that makes the rebuttal
     traceable in the UI, not just a vague "I disagree").
   - **Proposer** revises in response, except after the final round.
   - After all rounds, **Moderator** synthesizes a JSON `AgreedPlan`: decision summary,
     constraints addressed, performance/security considerations, and open risks.
4. **Every turn is persisted and embedded** — SQLite for the transcript, Qdrant for semantic
   search over it.
5. **Download the plan** as `plan.md`, generated client-side from the already-fetched JSON.
6. **Browse history** and see related past debates surfaced automatically via vector search
   over the `debate_turns` collection.

## Stack

| Layer | Choice | Why |
|---|---|---|
| Backend | Python + FastAPI | Deliberately Python, to build AI-engineer-relevant skills rather than staying in Angular/TS comfort zone. |
| Frontend | Angular, standalone components + signals | Existing strength — used to build a real streaming UI, not just forms. |
| LLM providers | Groq → Cerebras → Gemini, automatic fallback | Three independent free-tier rate-limit buckets behind one `llm_client.py` abstraction; persona code never touches provider specifics. Claude API was evaluated and excluded — no ongoing free tier. |
| Embeddings | Local `sentence-transformers` (`all-MiniLM-L6-v2`) | Free, unlimited, no API key, no network round-trip per embed. |
| Vector DB | Qdrant, self-hosted via Docker | Free, unlimited, no account. |
| Relational store | SQLite via SQLAlchemy | Zero-signup, simpler than a hosted Mongo/Postgres for a solo project. |
| Orchestration | Hand-rolled `run_debate()` generator | No LangGraph/CrewAI/AutoGen — a plain bounded loop is easier to explain in an interview and impossible to accidentally run forever. |

No heavy agent framework was used on purpose: the debate loop is ~250 lines in
[`orchestrator.py`](backend/app/orchestration/orchestrator.py) and every step (who speaks,
what they retrieve, what gets persisted) is explicit and inspectable, rather than hidden
behind a framework's control flow.

## Key design decisions

- **Fixed-round debate, not open-ended.** `rounds_planned` (2-5, user-selectable at
  submission time) bounds the loop up front. An LLM-judged "is this good enough yet"
  termination condition was considered and rejected — it adds a failure mode (the judge
  itself can hang or loop) for a portfolio project that needs to reliably terminate and
  produce a downloadable artifact every time.
- **The Critic's rebuttal is structurally forced, not just prompted.** The Critic's system
  prompt requires it to reference a specific prior turn, and the orchestrator independently
  infers `critiques_turn_id` by matching the Critic's output against recent turn content.
  This makes "who is this agent disagreeing with" a queryable, renderable fact instead of
  something a reader has to infer from prose.
- **Retrieval happens per-turn, not once per session.** Each dimension agent's Qdrant query
  uses the *current* proposal text, filtered by that agent's `dimension_hint` — so as the
  proposal evolves round to round, retrieved grounding notes evolve with it instead of being
  fixed at session start.
- **LLM provider fallback is a hard requirement, not a nicety.** Free-tier rate limits
  (Groq ~1K req/day, Gemini 100-1K/day depending on model) are easy to exhaust during active
  development of a multi-call-per-debate system. `llm_client.py` tries Groq → Cerebras →
  Gemini in order and falls back transparently on any error or missing key, so development
  doesn't stall on a single provider's daily cap.
- **Retry resumes cleanly, it doesn't duplicate.** If a debate fails partway (provider
  exhaustion, Qdrant briefly down), re-streaming the same session clears its partial turns
  and plan server-side (`reset_session_for_retry`) before restarting, rather than appending a
  second attempt's turns alongside the first's in the transcript.

## Local setup

```powershell
# 1. Qdrant
docker compose up -d

# 2. Backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # fill in GROQ_API_KEY (free, no card: console.groq.com)

# 3. Seed the concept knowledge base (76 notes)
python -m app.retrieval.concept_seeding.seed_concepts

# 4. Run the API
uvicorn app.main:app --reload --port 8000
```

```powershell
# 5. Frontend (separate terminal)
cd frontend
npm install
npm start   # serves on http://localhost:4200
```

## Verify

```powershell
curl http://localhost:8000/health

# Create a session (returns a structured ProblemBrief)
curl -X POST http://localhost:8000/api/v1/sessions -H "Content-Type: application/json" -d "{\"text\": \"Design a URL shortener for 1M reads/sec, budget under $500/month.\", \"rounds_planned\": 3}"

# Stream the full debate for that session id (SSE: turn_start, turn_end, plan, done, error)
curl -N http://localhost:8000/api/v1/sessions/{id}/stream

# Fetch the full transcript + agreed plan once complete
curl http://localhost:8000/api/v1/sessions/{id}

# Cross-session recall: similar past debates
curl http://localhost:8000/api/v1/sessions/{id}/related
```

Or just open `http://localhost:4200`, submit a prompt, and watch the transcript stream live.

## API

| Endpoint | Purpose |
|---|---|
| `POST /api/v1/sessions` | Create a session from free text (`rounds_planned` 2-5, default 3). |
| `POST /api/v1/sessions/upload` | Create a session from an uploaded `.txt`/`.md`/`.pdf`. |
| `GET /api/v1/sessions` | List past sessions. |
| `GET /api/v1/sessions/{id}` | Full transcript + agreed plan for one session. |
| `GET /api/v1/sessions/{id}/stream` | SSE stream of the live debate. Also used to retry a `failed` session. |
| `GET /api/v1/sessions/{id}/related` | Cross-session recall via vector search over past turns. |

## Repo structure

```
system-design-arena/
├── docker-compose.yml              # Qdrant only
├── backend/
│   └── app/
│       ├── api/routes/{sessions,debate}.py
│       ├── core/{llm_client.py, embeddings.py}
│       ├── orchestration/{personas.py, orchestrator.py, events.py}
│       ├── ingestion/{brief_normalizer.py, file_extractors.py}
│       ├── retrieval/{vector_store.py, concept_seeding/}
│       ├── persistence/{db.py, models.py, schemas.py}
│       └── services/{session_service.py, debate_service.py}
└── frontend/src/app/
    ├── core/{models/*, services/{session.service.ts, debate-stream.service.ts}}
    ├── features/{problem-input/, debate-arena/, history/}
    └── shared/{persona-badge/, related-sessions/, services/plan-export.service.ts}
```

## Status

Weeks 1-4 of the original build plan are complete: brief normalization, the full six-persona
debate loop with retrieval-per-turn, the Angular streaming UI, cross-session recall, an
expanded concept KB, user-selectable round count, and retry-on-failure. See `git log` for the
week-by-week history. Deployment (GitHub Pages + Render) is next.

A defined but not-yet-built extension exists for a second "delivery debate" phase
(PM/Developer/QA/Architect personas negotiating a shipping timeline off the agreed
architecture) — see the project's internal planning notes if picking this back up.
