from functools import lru_cache

from google import genai
from google.genai import types as genai_types

from app.config import get_settings

EMBEDDING_DIM = 768
_MODEL_NAME = "gemini-embedding-001"


@lru_cache
def _get_client() -> genai.Client:
    settings = get_settings()
    return genai.Client(api_key=settings.gemini_api_key)


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = _get_client().models.embed_content(
        model=_MODEL_NAME,
        contents=texts,
        config=genai_types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIM),
    )
    return [e.values for e in response.embeddings]
