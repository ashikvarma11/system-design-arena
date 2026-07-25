import uuid
from functools import lru_cache

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams

from app.config import get_settings
from app.core.embeddings import EMBEDDING_DIM, embed_text

CONCEPTS_COLLECTION = "concepts"
DEBATE_TURNS_COLLECTION = "debate_turns"


@lru_cache
def get_qdrant_client() -> QdrantClient:
    settings = get_settings()
    return QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)


def ensure_collections() -> None:
    client = get_qdrant_client()
    existing = {c.name for c in client.get_collections().collections}
    for name in (CONCEPTS_COLLECTION, DEBATE_TURNS_COLLECTION):
        if name not in existing:
            client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
            )


def upsert_concept(concept_id: str, text: str, payload: dict) -> None:
    client = get_qdrant_client()
    vector = embed_text(text)
    client.upsert(
        collection_name=CONCEPTS_COLLECTION,
        points=[PointStruct(id=concept_id, vector=vector, payload=payload)],
    )


def search_concepts(query: str, limit: int = 3, dimension_hint: str | None = None) -> list[dict]:
    client = get_qdrant_client()
    vector = embed_text(query)
    query_filter = None
    if dimension_hint:
        query_filter = Filter(
            must=[FieldCondition(key="dimension_hint", match=MatchValue(value=dimension_hint))]
        )
    results = client.query_points(
        collection_name=CONCEPTS_COLLECTION,
        query=vector,
        limit=limit,
        query_filter=query_filter,
    )
    return [{"score": p.score, **p.payload} for p in results.points]


def upsert_debate_turn(turn_id: str, content: str, payload: dict) -> None:
    client = get_qdrant_client()
    vector = embed_text(content)
    client.upsert(
        collection_name=DEBATE_TURNS_COLLECTION,
        points=[PointStruct(id=turn_id, vector=vector, payload=payload)],
    )


def search_debate_turns(query: str, limit: int = 10, exclude_session_id: str | None = None) -> list[dict]:
    client = get_qdrant_client()
    vector = embed_text(query)
    query_filter = None
    if exclude_session_id:
        query_filter = Filter(
            must_not=[FieldCondition(key="session_id", match=MatchValue(value=exclude_session_id))]
        )
    results = client.query_points(
        collection_name=DEBATE_TURNS_COLLECTION,
        query=vector,
        limit=limit,
        query_filter=query_filter,
    )
    return [{"score": p.score, **p.payload} for p in results.points]


def new_point_id() -> str:
    return str(uuid.uuid4())
