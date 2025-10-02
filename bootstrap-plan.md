# VPS Bootstrap Plan

Complete automation plan for setting up new VPS. Each step clearly indicates where to execute.

## Step 1: Initial VPS Access (Mac)

```bash
ssh root@45.32.117.48
```

Enter password when prompted. Stay connected for next steps.

## Step 2: Clone Repository (VPS)

Repository is public, so we can clone immediately:

```bash
cd /root
git clone https://github.com/kiraistakenlol/soul-mirror.git
cd soul-mirror
```

## Step 3: Run Bootstrap Script (VPS)

```bash
chmod +x bootstrap.sh
./bootstrap.sh
```

This installs:
- Docker, Docker Compose
- nginx
- Node.js, npm
- Claude Code
- git, nano, ufw (firewall)
- Generates SSH key for GitHub
- Configures firewall

The script will display VPS SSH public key at the end.

## Step 4: Add VPS SSH Key to GitHub (Mac)

Copy the SSH public key displayed by bootstrap script.

1. Open https://github.com/settings/keys
2. Click "New SSH key"
3. Paste the key
4. Name it "Soul Mirror VPS"
5. Click "Add SSH key"

## Step 5: Configure Git to Use SSH (VPS)

```bash
cd /root/soul-mirror
git remote set-url origin git@github.com:kiraistakenlol/soul-mirror.git
git pull
```

## Step 6: Setup Passwordless SSH Access (Mac)

```bash
# Generate SSH key on Mac if you don't have one
ssh-keygen -t ed25519 -C "mac@soul-mirror"

# Copy to VPS
ssh-copy-id root@45.32.117.48

# Test (should not ask for password)
ssh root@45.32.117.48
```

## Step 7: Configure Services (VPS)

```bash
cd /root/soul-mirror

# Backend environment
cat > apps/backend/.env << 'EOF'
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=YOUR_API_KEY_HERE
PORT=8080
ENVIRONMENT=production
EOF

# Telegram bot environment
cat > apps/telegram-bot/.env << 'EOF'
TELEGRAM_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
OPENAI_API_KEY=YOUR_OPENAI_KEY_HERE
BACKEND_URL=http://backend:8080
EOF

# Configure nginx
cp infra/nginx.conf /etc/nginx/sites-available/soulmirror
ln -s /etc/nginx/sites-available/soulmirror /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

## Step 8: Start Services (VPS)

```bash
cd /root/soul-mirror
docker-compose up -d
```

## Step 9: Verify Deployment (VPS)

```bash
docker-compose ps
docker-compose logs -f
curl http://45.32.117.48/api/status
```

## Done!

Access: http://45.32.117.48

---

## Alternative: Fully Automated from Mac

If you want to automate even more, you could create a script that does steps 1-3 automatically:

```bash
./scripts/setup-vps-initial.sh 45.32.117.48
```

This would:
- SSH into VPS
- Clone repo
- Run bootstrap.sh
- Display SSH key for GitHub

Let me know if you want me to create this script.
