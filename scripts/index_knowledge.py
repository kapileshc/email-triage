import json
from pathlib import Path

from app.rag.qdrant_store import index_documents


def main():
    rows = json.loads(Path("data/approved_knowledge.json").read_text(encoding="utf-8"))
    count = index_documents(rows)
    print(f"Indexed {count} approved knowledge records into Qdrant Cloud")


if __name__ == "__main__":
    main()
