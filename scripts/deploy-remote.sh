#!/bin/bash
# Remote deploy script (runs on local machine, triggers VPS deploy)

set -e

echo "🚀 Deploying to VPS (45.76.89.58)..."
echo ""

ssh root@45.76.89.58 << 'ENDSSH'
cd /root/soul-mirror
git pull
docker-compose up -d --build
echo ""
echo "✅ Deployment complete!"
ENDSSH

echo ""
echo "🌐 Visit: http://45.76.89.58"
