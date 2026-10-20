import uuid

from qdrant_client import QdrantClient, models

from app.config import settings
from app.embeddings.azure_foundry import embed_text, embed_texts
from app.schemas import Evidence


def get_client() -> QdrantClient:
    if not settings.qdrant_url:
        raise RuntimeError("QDRANT_URL is not configured")
    return QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None, timeout=15)


def retrieve(query: str, k: int | None = None) -> list[Evidence]:
    try:
        response = get_client().query_points(
            collection_name=settings.qdrant_collection,
            query=embed_text(query),
            limit=k or settings.top_k,
            with_payload=True,
        )
    except Exception:
        return []

    return [
        Evidence(
            source=str((point.payload or {}).get("source", "unknown")),
            text=str((point.payload or {}).get("text", "")),
            score=float(point.score) if point.score is not None else None,
        )
        for point in response.points
    ]


def index_documents(rows: list[dict]) -> int:
    if not rows:
        return 0

    texts = [row["text"] for row in rows]
    vectors = embed_texts(texts)
    client = get_client()

    if not client.collection_exists(settings.qdrant_collection):
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=models.VectorParams(size=len(vectors[0]), distance=models.Distance.COSINE),
        )

    points = []
    for row, vector in zip(rows, vectors):
        points.append(
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "source": row.get("source", "unknown"),
                    "title": row.get("title", ""),
                    "text": row["text"],
                },
            )
        )
    client.upsert(collection_name=settings.qdrant_collection, points=points, wait=True)
    return len(points)
