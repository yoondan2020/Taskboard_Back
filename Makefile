.PHONY: dev kill-8000 restart

kill-8000:
	lsof -ti :8000 | xargs kill -9 || true

dev:
	./.venv/bin/python -m uvicorn app.main:app --reload

restart: kill-8000 dev
