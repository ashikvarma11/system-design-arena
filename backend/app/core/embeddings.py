from functools import lru_cache

from sentence_transformers import SentenceTransformer

EMBEDDING_DIM = 384
_MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache
def _get_model() -> SentenceTransformer:
    return SentenceTransformer(_MODEL_NAME)


def embed_text(text: str) -> list[float]:
    return _get_model().encode(text, normalize_embeddings=True).tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    return _get_model().encode(texts, normalize_embeddings=True).tolist()
