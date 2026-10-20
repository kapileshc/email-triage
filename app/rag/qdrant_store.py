from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from app.config import settings
from app.schemas import Evidence


def _embeddings():
    return HuggingFaceEmbeddings(model_name=settings.embedding_model)


def get_store() -> QdrantVectorStore:
    client = QdrantClient(url=settings.qdrant_url)
    return QdrantVectorStore(client=client, collection_name=settings.qdrant_collection, embedding=_embeddings())


def retrieve(query: str, k: int | None = None) -> list[Evidence]:
    try:
        store = get_store()
        docs = store.similarity_search_with_score(query, k=k or settings.top_k)
    except Exception:
        return []

    return [Evidence(source=str(doc.metadata.get("source", "unknown")), text=doc.page_content, score=float(score)) for doc, score in docs]
