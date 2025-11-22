#!/bin/bash
# Start all development services: docker-compose, fastapi server, and celery worker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Trap Ctrl+C to cleanup
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    docker-compose down
    kill %1 %2 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${GREEN}Starting PostgreSQL and Redis...${NC}"
docker-compose up -d

echo -e "${GREEN}Starting Celery worker...${NC}"
python -m app.cli worker &
WORKER_PID=$!

echo -e "${GREEN}Starting FastAPI server...${NC}"
python -m app.cli server &
SERVER_PID=$!

echo -e "${GREEN}✓ All services started!${NC}"
echo -e "  - API: http://localhost:8000"
echo -e "  - Docs: http://localhost:8000/docs"
echo -e "  - PostgreSQL: localhost:5432"
echo -e "  - Redis: localhost:6379"
echo -e "\n${YELLOW}Press Ctrl+C to stop all services${NC}\n"

# Wait for both processes
wait $WORKER_PID $SERVER_PID
