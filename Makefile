install:
	pip install -r requirements.txt

qdrant:
	docker compose up -d qdrant

index:
	python scripts/index_knowledge.py

api:
	uvicorn app.main:app --reload --port 8000

ui:
	streamlit run streamlit_app.py

test:
	pytest -q
