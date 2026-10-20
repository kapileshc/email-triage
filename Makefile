install:
	pip install -r requirements.txt

index:
	python scripts/index_knowledge.py

api:
	uvicorn app.main:app --reload --port 8001

frontend-install:
	cd frontend && npm install

frontend:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

test:
	pytest -q
