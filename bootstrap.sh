#!/bin/bash
# Bootstrap script for Soul Mirror VPS deployment

set -e

echo "🚀 Starting Soul Mirror VPS bootstrap..."

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install Node.js 20.x
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs

# Verify Node.js
echo "✓ Node.js installed: $(node --version)"
echo "✓ npm installed: $(npm --version)"

# Install Claude Code
echo "📦 Installing Claude Code..."
npm install -g @anthropic-ai/claude-code

# Verify Claude Code
echo "✓ Claude Code installed"
claude doctor || true

# Install Docker
echo "📦 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Install Docker Compose
echo "📦 Installing Docker Compose..."
apt install -y docker-compose

# Install nginx
echo "📦 Installing nginx..."
apt install -y nginx

# Install git (if not already installed)
apt install -y git

echo ""
echo "✅ Bootstrap complete!"
echo ""
echo "Next steps:"
echo "1. Authenticate Claude: cd /root/soul-mirror && claude"
echo "2. Follow authentication prompts"
echo "3. Run: cat DEPLOY.md"
echo "4. Ask Claude to execute the deployment"
