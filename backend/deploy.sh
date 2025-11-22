#!/bin/bash
set -e

# Deploy script for spoon-transcribing backend
# Deploys to ~/spoon-backend on the production server

DEPLOY_DIR="$HOME/spoon-backend"
REPO_URL="https://github.com/yourusername/spoon-transcribing.git"  # Update this

echo "🚀 Deploying spoon-transcribing backend..."

# Create deploy directory if it doesn't exist
mkdir -p "$DEPLOY_DIR"
cd "$DEPLOY_DIR"

# If this is a fresh deploy, clone the repo
if [ ! -d ".git" ]; then
    echo "📦 Cloning repository..."
    cd ..
    rm -rf spoon-backend
    git clone "$REPO_URL" spoon-backend
    cd spoon-backend/backend
else
    echo "📥 Pulling latest changes..."
    git pull origin master
    cd backend
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo "   Please create $DEPLOY_DIR/backend/.env with your configuration"
    echo ""
    echo "   Required variables:"
    echo "   - ZOOM_CLIENT_ID"
    echo "   - ZOOM_CLIENT_SECRET"
    echo "   - ZOOM_WEBHOOK_SECRET_TOKEN"
    echo "   - OPENAI_API_KEY (or OPENROUTER_API_KEY)"
    echo "   - RESEND_API_KEY"
    echo ""
    exit 1
fi

# Build and start services
echo "🔨 Building Docker images..."
docker compose -f docker-compose.prod.yml build

echo "🛑 Stopping existing services..."
docker compose -f docker-compose.prod.yml down || true

echo "🚀 Starting services..."
docker compose -f docker-compose.prod.yml up -d

echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service status
echo "📊 Service status:"
docker compose -f docker-compose.prod.yml ps

# Show logs
echo ""
echo "📋 Recent logs:"
docker compose -f docker-compose.prod.yml logs --tail=20

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🔗 API available at: http://localhost:8001"
echo "📚 Docs available at: http://localhost:8001/docs"
echo ""
echo "Useful commands:"
echo "  docker compose -f docker-compose.prod.yml logs -f        # Follow logs"
echo "  docker compose -f docker-compose.prod.yml ps             # Check status"
echo "  docker compose -f docker-compose.prod.yml down           # Stop services"
echo "  docker compose -f docker-compose.prod.yml restart api    # Restart API"
