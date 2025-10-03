# Infrastructure & Deployment

VPS deployment configuration for Soul Mirror.

## Server Details

- Provider: Vultr (https://my.vultr.com/)
- Location: Frankfurt
- IP: 45.32.117.48
- OS: Ubuntu
- Access: `ssh root@45.32.117.48`

## Bootstrap New VPS

**Automated setup from your Mac:**

**1. Run setup script**
```bash
./scripts/setup-vps.sh 45.32.117.48
```

This will:
- Generate SSH key on Mac (if needed)
- Setup passwordless SSH access to VPS
- Upload and run bootstrap.sh on VPS
- Install Docker, nginx, Node.js, Claude Code, git, firewall
- Generate SSH key on VPS for GitHub
- Display VPS public key

**2. Add VPS SSH key to GitHub**

The script will display the VPS public key. Copy it and:
- Go to https://github.com/settings/keys
- Click "New SSH key"
- Paste the key, name it "Soul Mirror VPS"
- Click "Add SSH key"

**3. Clone repository on VPS**
```bash
ssh root@45.32.117.48
cd /root
git clone git@github.com:YOUR_USERNAME/soul-mirror.git
cd soul-mirror
```

**4. Continue with deployment**

Follow the [Initial Setup](#initial-setup) section below to configure services.

---

**Manual setup (if automated script fails):**

<details>
<summary>Click to expand manual steps</summary>

**1. SSH into VPS**
```bash
ssh root@45.32.117.48
```

**2. Download and run bootstrap**
```bash
curl -o bootstrap.sh https://raw.githubusercontent.com/YOUR_USERNAME/soul-mirror/master/bootstrap.sh
chmod +x bootstrap.sh
./bootstrap.sh
```

**3. Setup SSH from Mac**
```bash
# On Mac
ssh-keygen -t ed25519 -C "mac@soul-mirror"
ssh-copy-id root@45.32.117.48
```

**4. Add VPS key to GitHub**
```bash
# On VPS, display public key
cat ~/.ssh/id_ed25519.pub
# Add to https://github.com/settings/keys
```

**5. Clone repository**
```bash
# On VPS
cd /root
git clone git@github.com:YOUR_USERNAME/soul-mirror.git
```

</details>

## Architecture

```
Internet (port 80)
    ↓
nginx (reverse proxy)
    ├─→ /api/* → localhost:8080 (backend container)
    └─→ /*     → localhost:3000 (frontend container)
```

**Components:**
- nginx: Listens on port 80, routes `/api/*` to backend, everything else to frontend
- Docker Compose: Orchestrates backend (Python/FastAPI) and frontend (React/Vite) services
- Backend reads `.env` from `apps/backend/.env`

## Initial Setup

**Prerequisites:** Repository cloned to `/root/soul-mirror`, `bootstrap.sh` executed (installs Docker, nginx, Claude Code)

**1. Install text editor**
```bash
apt install nano -y   # or: apt install vim -y
```

**2. Configure backend environment**
```bash
cd apps/backend
cat > .env << 'EOF'
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=<YOUR_API_KEY>
PORT=8080
ENVIRONMENT=production
EOF
cd ../..
```

**3. Configure nginx**
```bash
cp infra/nginx.conf /etc/nginx/sites-available/soulmirror
ln -s /etc/nginx/sites-available/soulmirror /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

**4. Enable IPv6 (required for Docker)**
```bash
# On Vultr dashboard: Settings → IPv6 → Enable IPv6
# Then on VPS:
systemctl restart networking
# Verify IPv6 is working:
ping6 -c 3 google.com
```

**5. Open firewall**
```bash
ufw allow 80/tcp
ufw allow 443/tcp
ufw status
```

**6. Start services**
```bash
docker-compose up -d
```

**7. Verify**
```bash
docker-compose ps
docker-compose logs -f
curl http://45.32.117.48/api/status
```

## Deployment Scripts

**Local → VPS:** `./scripts/deploy-remote.sh` - SSH to VPS, pull code, rebuild containers

**On VPS:** `./scripts/deploy.sh` - Pull code, rebuild containers (run directly on server)

## Management

**View logs**
```bash
docker-compose logs -f           # all services
docker-compose logs backend      # backend only
docker-compose logs frontend     # frontend only
```

**Restart services**
```bash
docker-compose restart           # all
docker-compose restart backend   # specific service
```

**Apply code changes**
```bash
docker-compose up -d --build
```

**Stop everything**
```bash
docker-compose down
```

## Troubleshooting

**Nginx issues**
```bash
systemctl status nginx
nginx -t
systemctl restart nginx
journalctl -u nginx -f
```

**Docker issues**
```bash
docker-compose ps
docker-compose logs backend
docker-compose up -d --build
```

**Common issues**
- Port conflicts: `netstat -tlnp | grep :8080` or `:3000`
- Firewall blocking: `ufw status` (ensure port 80/443 allowed)
- API not responding: Check backend logs and `.env` has API key
- Changes not showing: Rebuild with `docker-compose up -d --build`
- Docker build fails with "network is unreachable": Enable IPv6 in Vultr dashboard

## Future: Add Domain

**When domain ready (e.g., soulmirror.kira.dev):**

**1. Configure DNS at registrar**
- Add wildcard A record: `*.kira.dev` → `45.32.117.48`
- Wait 5-60 minutes for propagation

**2. Update nginx**
```bash
# Edit /etc/nginx/sites-available/soulmirror
# Change: server_name 45.32.117.48;
# To:     server_name soulmirror.kira.dev;
systemctl reload nginx
```

**3. Add SSL (HTTPS)**
```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx  # Follow prompts
```

Result: Access via https://soulmirror.kira.dev with auto-renewing SSL

## Files

- `nginx.conf` - Reverse proxy configuration
- `../docker-compose.yml` - Container orchestration
- `../apps/backend/Dockerfile` - Backend image
- `../apps/frontend/Dockerfile` - Frontend image
- `../scripts/deploy.sh` - Deploy script (runs on VPS)
- `../scripts/deploy-remote.sh` - Deploy script (runs locally, triggers VPS)
