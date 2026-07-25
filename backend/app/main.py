from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import debate, sessions
from app.config import get_settings
from app.persistence.db import init_db

settings = get_settings()

app = FastAPI(title="System Design Arena API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router)
app.include_router(debate.router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health():
    return {"status": "ok"}
