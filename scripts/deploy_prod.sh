#!/usr/bin/env bash
set -euo pipefail

HOST="87.242.103.118"
USER="${DEPLOY_USER:-user1}"
SSH_KEY="${SSH_KEY:-id_ed25519_sber}"
REMOTE_DIR="/home/$USER/spoon-backend"
ACME_EMAIL="${ACME_EMAIL:-admin@aprivai.com}"
TRAEFIK_DIR="/home/$USER/traefik"

echo "🚀 Starting deployment to $HOST..."

# Create directories with proper permissions
echo "📁 Creating directories..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$USER@$HOST" "sudo mkdir -p $REMOTE_DIR $TRAEFIK_DIR && sudo chown -R $USER:$USER $REMOTE_DIR $TRAEFIK_DIR"

# Install docker if not present
echo "🐳 Checking Docker installation..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$USER@$HOST" "bash -lc 'if ! command -v docker >/dev/null 2>&1; then echo \"Installing Docker...\"; sudo apt-get update -y; sudo apt-get install -y ca-certificates curl gnupg; sudo install -m 0755 -d /etc/apt/keyrings; curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg; sudo chmod a+r /etc/apt/keyrings/docker.gpg; echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \$(. /etc/os-release && echo \"\$VERSION_CODENAME\") stable\" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null; sudo apt-get update -y; sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin; sudo systemctl enable --now docker; sudo usermod -aG docker $USER; fi'"

# Setup traefik acme.json
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$USER@$HOST" "sudo touch $TRAEFIK_DIR/acme.json && sudo chmod 600 $TRAEFIK_DIR/acme.json && sudo chown $USER:$USER $TRAEFIK_DIR/acme.json"

# Sync files
echo "📦 Syncing files..."
rsync -az --delete --exclude='.venv' --exclude='__pycache__' --exclude='.claude' -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" backend/ "$USER@$HOST:$REMOTE_DIR/"

# Copy .env file
echo "🔐 Copying environment file..."
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no backend/.env "$USER@$HOST:$REMOTE_DIR/.env"

# Run migrations
echo "🔄 Running database migrations..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$USER@$HOST" "cd $REMOTE_DIR && sudo ACME_EMAIL='$ACME_EMAIL' docker compose -f $REMOTE_DIR/docker-compose.prod.yaml run --rm migrate"

# Build and start services
echo "🔨 Building and starting services..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$USER@$HOST" "cd $REMOTE_DIR && sudo ACME_EMAIL='$ACME_EMAIL' docker compose -f $REMOTE_DIR/docker-compose.prod.yaml up -d --build --remove-orphans"

# Show status and logs
echo "📊 Service status and logs..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$USER@$HOST" "cd $REMOTE_DIR && sudo docker compose -f $REMOTE_DIR/docker-compose.prod.yaml ps && sudo docker compose -f $REMOTE_DIR/docker-compose.prod.yaml logs --no-log-prefix --timestamps --tail=100"

echo ""
echo "✅ Deployment complete!"
echo "🔗 API: https://api.transcribe.aprivai.com"