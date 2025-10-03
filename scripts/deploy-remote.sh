#!/bin/bash
# Remote deploy script (runs on local machine, triggers VPS deploy)

set -e

echo "🚀 Deploying to VPS (45.32.117.48)..."
echo ""

ssh root@45.32.117.48 'cd /root/soul-mirror && ./scripts/deploy.sh'

echo ""
echo "🌐 Visit: http://45.32.117.48"
