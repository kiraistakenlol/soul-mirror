#!/bin/bash
# Setup VPS from Mac - automates SSH access and bootstrap

set -e

VPS_IP="${1:-45.32.117.48}"

echo "🚀 Setting up VPS at $VPS_IP"
echo ""

# Check if SSH key exists on Mac
if [ ! -f ~/.ssh/id_ed25519 ]; then
    echo "🔑 Generating SSH key on Mac..."
    ssh-keygen -t ed25519 -C "mac@soul-mirror" -f ~/.ssh/id_ed25519 -N ""
    echo "✓ SSH key generated"
else
    echo "✓ SSH key already exists on Mac"
fi

echo ""
echo "📤 Copying SSH key to VPS..."
echo "You'll need to enter VPS password..."
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@$VPS_IP

echo ""
echo "✓ SSH key copied. Testing connection..."
ssh root@$VPS_IP "echo '✓ SSH connection successful'"

echo ""
echo "📥 Uploading bootstrap script to VPS..."
scp bootstrap.sh root@$VPS_IP:/root/bootstrap.sh

echo ""
echo "🔧 Running bootstrap script on VPS..."
ssh root@$VPS_IP "chmod +x /root/bootstrap.sh && /root/bootstrap.sh"

echo ""
echo "✅ VPS setup complete!"
echo ""
echo "Next steps:"
echo "1. The SSH public key from VPS was displayed above"
echo "2. Add it to GitHub: https://github.com/settings/keys"
echo "3. SSH into VPS: ssh root@$VPS_IP"
echo "4. Clone repo: cd /root && git clone git@github.com:YOUR_USERNAME/soul-mirror.git"
echo "5. Follow infra/README.md for deployment"
