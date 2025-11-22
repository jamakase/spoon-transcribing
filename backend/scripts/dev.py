#!/usr/bin/env python
"""Run all backend services in dev mode."""

import subprocess
import sys
import signal
import os

processes = []


def cleanup(signum, frame):
    print("\nShutting down...")
    for p in processes:
        p.terminate()
    # Stop docker-compose
    subprocess.run(["docker-compose", "down"], cwd=os.path.dirname(os.path.dirname(__file__)))
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    root_dir = os.path.dirname(os.path.dirname(__file__))

    # Start docker-compose
    print("Starting PostgreSQL and Redis...")
    subprocess.run(["docker-compose", "up", "-d"], cwd=root_dir, check=True)

    # Start Celery worker
    print("Starting Celery worker...")
    worker = subprocess.Popen(
        ["uv", "run", "celery", "-A", "app.celery_app", "worker", "--loglevel=info"],
        cwd=root_dir
    )
    processes.append(worker)

    # Start FastAPI
    print("Starting FastAPI server...")
    api = subprocess.Popen(
        ["uv", "run", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd=root_dir
    )
    processes.append(api)

    print("\n✓ All services started!")
    print("  - API: http://localhost:8000")
    print("  - Docs: http://localhost:8000/docs")
    print("  - PostgreSQL: localhost:5432")
    print("  - Redis: localhost:6379")
    print("\nPress Ctrl+C to stop all services\n")

    # Wait for processes
    try:
        api.wait()
    except KeyboardInterrupt:
        cleanup(None, None)


if __name__ == "__main__":
    main()
