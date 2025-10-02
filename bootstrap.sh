#!/bin/bash
# Bootstrap script for Soul Mirror VPS deployment

set -e

echo "🚀 Starting Soul Mirror VPS bootstrap..."

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install essential tools
echo "📦 Installing essential tools..."
apt install -y git nano curl ufw

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

# Setup SSH key for GitHub
echo "🔑 Setting up SSH key for GitHub..."
if [ ! -f ~/.ssh/id_ed25519 ]; then
    ssh-keygen -t ed25519 -C "vps@soul-mirror" -f ~/.ssh/id_ed25519 -N ""
    echo "✓ SSH key generated"
else
    echo "✓ SSH key already exists"
fi

# Configure git
echo "📝 Configuring git..."
git config --global user.email "vps@soul-mirror"
git config --global user.name "Soul Mirror VPS"

# Setup firewall
echo "🔒 Configuring firewall..."
ufw --force enable
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
echo "✓ Firewall configured"

echo ""
echo "✅ Bootstrap complete!"
echo ""
echo "🔑 Your SSH public key (add this to GitHub):"
echo "──────────────────────────────────────────────"
cat ~/.ssh/id_ed25519.pub
echo "──────────────────────────────────────────────"
echo ""
echo "Next steps:"
echo "1. Add the SSH key above to GitHub: https://github.com/settings/keys"
echo "2. Clone repository: git clone git@github.com:YOUR_USERNAME/soul-mirror.git"
echo "3. Follow infra/README.md for deployment"
