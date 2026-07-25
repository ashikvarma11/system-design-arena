import uuid

from app.retrieval.concept_seeding.concepts_data import CONCEPTS
from app.retrieval.vector_store import ensure_collections, upsert_concept

_NAMESPACE = uuid.UUID("a3f1e7b0-6c2d-4a9e-9b3f-1d2c3e4f5a6b")


def _point_id(slug: str) -> str:
    return str(uuid.uuid5(_NAMESPACE, slug))


def seed() -> None:
    ensure_collections()
    for concept in CONCEPTS:
        payload = {
            "concept_id": concept["id"],
            "title": concept["title"],
            "text": concept["text"],
            "tags": concept["tags"],
            "dimension_hint": concept["dimension_hint"],
        }
        upsert_concept(_point_id(concept["id"]), concept["text"], payload)
        print(f"seeded: {concept['id']}")
    print(f"\nDone. Seeded {len(CONCEPTS)} concepts.")


if __name__ == "__main__":
    seed()
