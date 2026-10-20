import json
from pathlib import Path

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore

from app.config import settings


def main():
    rows = json.loads(Path("data/approved_knowledge.json").read_text(encoding="utf-8"))
    docs = [Document(page_content=row["text"], metadata={"source": row["source"], "title": row["title"]}) for row in rows]
    embeddings = HuggingFaceEmbeddings(model_name=settings.embedding_model)
    QdrantVectorStore.from_documents(documents=docs, embedding=embeddings, url=settings.qdrant_url, collection_name=settings.qdrant_collection, force_recreate=True)
    print(f"Indexed {len(docs)} records into {settings.qdrant_collection}")


if __name__ == "__main__":
    main()
