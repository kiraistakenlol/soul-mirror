#!/bin/bash
# Deploy script (runs on VPS)

set -e

echo "🚀 Deploying Soul Mirror..."

cd /root/soul-mirror

echo "📥 Pulling latest code..."
git pull

echo "🐳 Building and restarting containers..."
docker-compose up -d --build

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Verify:"
echo "  docker-compose ps"
echo "  docker-compose logs -f"
