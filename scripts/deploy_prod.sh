#!/usr/bin/env bash
set -euo pipefail

HOST="87.242.103.118"
USER="${DEPLOY_USER:-user1}"
SSH_KEY="${SSH_KEY:-id_ed25519_sber}"
REMOTE_DIR="/opt/spoon/backend"
ACME_EMAIL="${ACME_EMAIL:-admin@aprivai.com}"
TRAEFIK_DIR="/opt/spoon/traefik"

ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$USER@$HOST" "bash -lc 'sudo mkdir -p $REMOTE_DIR $TRAEFIK_DIR'"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$USER@$HOST" "bash -lc 'set -e; if ! command -v docker >/dev/null 2>&1; then sudo apt-get update -y; sudo apt-get install -y ca-certificates curl gnupg; sudo install -m 0755 -d /etc/apt/keyrings; curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg; echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release; echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null; sudo apt-get update -y; sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin; sudo systemctl enable --now docker; fi; sudo touch $TRAEFIK_DIR/acme.json; sudo chmod 600 $TRAEFIK_DIR/acme.json'"
rsync -az --delete -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" backend/ "$USER@$HOST:$REMOTE_DIR/"
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no backend/.env "$USER@$HOST:$REMOTE_DIR/.env"

ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$USER@$HOST" "cd $REMOTE_DIR && ACME_EMAIL='$ACME_EMAIL' docker compose -f docker-compose.prod.yaml run --rm migrate"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$USER@$HOST" "cd $REMOTE_DIR && ACME_EMAIL='$ACME_EMAIL' docker compose -f docker-compose.prod.yaml up -d --build --remove-orphans"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$USER@$HOST" "cd $REMOTE_DIR && docker compose -f docker-compose.prod.yaml ps && docker compose -f docker-compose.prod.yaml logs --no-log-prefix --timestamps --tail=100"