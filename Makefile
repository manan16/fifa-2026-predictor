PYTHON ?= python3

.PHONY: install backend frontend migrate seed sync test docker-up docker-down

install:
	cd backend && $(PYTHON) -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install

backend:
	cd backend && $(PYTHON) run.py

frontend:
	cd frontend && npm run dev

migrate:
	cd backend && $(PYTHON) -m app.db.migrate

seed:
	cd backend && $(PYTHON) -m app.db.seed

sync:
	cd backend && $(PYTHON) -m app.db.sync

test:
	cd backend && $(PYTHON) -m pytest

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down
