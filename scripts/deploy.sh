#!/bin/bash
# Deploy script (runs on VPS)

set -e

echo "🚀 Deploying Soul Mirror..."

cd /root/soul-mirror

echo "📥 Pulling latest code..."
git pull

echo "🛑 Stopping containers..."
docker-compose down

echo "🐳 Building and starting containers..."
docker-compose --env-file .env.production up -d --build

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Verify:"
echo "  docker-compose ps"
echo "  docker-compose logs -f"
