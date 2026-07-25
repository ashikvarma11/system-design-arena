# System Design Arena

Submit a system design prompt (free text or an uploaded architecture-decision file) and
watch multiple LLM personas debate it across constraints, performance, security, and
feedback — one agent explicitly critiquing another — converging on an agreed plan.

Entire stack runs on free tiers only: no paid API keys, no required credit card.

## Status: Week 1

FastAPI skeleton, SQLite models, Qdrant (Docker) vector store, a 57-note concept
knowledge base, file upload with PDF extraction, and the first Groq-backed brief
normalizer. `POST /api/v1/sessions` (or `/sessions/upload`) takes raw input and returns
a stored, structured `ProblemBrief` (`goals`, `constraints`, `non_goals`).

## Stack

- **Backend**: Python + FastAPI, SQLAlchemy (SQLite), Qdrant (self-hosted via Docker),
  local `sentence-transformers` embeddings, Groq (primary LLM, Cerebras/Gemini planned
  as fallback providers).
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
curl -X POST http://localhost:8000/api/v1/sessions -H "Content-Type: application/json" -d "{\"text\": \"Design a URL shortener for 1M reads/sec, budget under $500/month.\"}"
```
