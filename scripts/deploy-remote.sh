#!/bin/bash
# Remote deploy script (runs on local machine, triggers VPS deploy)

set -e

echo "🚀 Deploying to VPS (45.32.117.48)..."
echo ""

ssh root@45.32.117.48 << 'ENDSSH'
cd /root/soul-mirror
git pull
docker-compose up -d --build
echo ""
echo "✅ Deployment complete!"
ENDSSH

echo ""
echo "🌐 Visit: http://45.32.117.48"
