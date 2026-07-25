# System Design Arena

Submit a system design prompt (free text or an uploaded architecture-decision file) and
watch multiple LLM personas debate it across constraints, performance, security, and
feedback — one agent explicitly critiquing another — converging on an agreed plan.

Entire stack runs on free tiers only: no paid API keys, no required credit card.

## Status: Week 2

Full multi-agent debate runs end-to-end. `POST /api/v1/sessions` (or `/sessions/upload`)
normalizes raw input into a structured `ProblemBrief`, then
`GET /api/v1/sessions/{id}/stream` (SSE) runs a bounded debate: Proposer/Architect kicks
off, Constraints/Performance/Security agents react each round (retrieving grounding notes
from the Qdrant concept KB first), a Critic explicitly rebuts one specific prior turn, the
Proposer revises, and after the fixed round count a Moderator synthesizes the final
`AgreedPlan`. Every turn is persisted to SQLite and embedded into Qdrant's `debate_turns`
collection.

## Stack

- **Backend**: Python + FastAPI, SQLAlchemy (SQLite), Qdrant (self-hosted via Docker),
  local `sentence-transformers` embeddings, LLM providers with automatic fallback:
  Groq (primary) -> Cerebras (high-volume secondary) -> Gemini (tertiary).
- **Frontend**: Angular (Week 3+).

## Local setup

```powershell
# 1. Qdrant
docker compose up -d

# 2. Backend
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # then fill in GROQ_API_KEY (free, no card: console.groq.com)

# 3. Seed the concept knowledge base
python -m app.retrieval.concept_seeding.seed_concepts

# 4. Run the API
uvicorn app.main:app --reload --port 8000
```

## Verify

```powershell
curl http://localhost:8000/health

# Create a session (returns a structured ProblemBrief)
curl -X POST http://localhost:8000/api/v1/sessions -H "Content-Type: application/json" -d "{\"text\": \"Design a URL shortener for 1M reads/sec, budget under $500/month.\"}"

# Stream the full debate for that session id (SSE: turn_start, turn_end, plan, done, error)
curl -N http://localhost:8000/api/v1/sessions/{id}/stream

# Fetch the full transcript + agreed plan once complete
curl http://localhost:8000/api/v1/sessions/{id}
```
