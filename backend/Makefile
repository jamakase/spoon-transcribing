.PHONY: dev server worker down help

help:
	@echo "Available commands:"
	@echo "  make dev       - Start all services (docker-compose, server, and worker)"
	@echo "  make server    - Start FastAPI server only"
	@echo "  make worker    - Start Celery worker only"
	@echo "  make down      - Stop all docker containers"

dev:
	./dev.sh

server:
	python -m app.cli server

worker:
	python -m app.cli worker

down:
	docker-compose down

ngrok:
	ngrok http 8001

test-streaming:
	python test_streaming.py

test-chat:
	python test_chat.py
