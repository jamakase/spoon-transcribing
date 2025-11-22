#!/usr/bin/env python
"""CLI commands for running the application."""

import sys
import uvicorn
from app.celery_app import celery_app


def run_server():
    """Start the FastAPI server."""
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )


def run_worker():
    """Start the Celery worker."""
    celery_app.worker_main([
        "worker",
        "--loglevel=info",
    ])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: cli.py [server|worker]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "server":
        run_server()
    elif command == "worker":
        run_worker()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
