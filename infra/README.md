# Infrastructure & Deployment

VPS deployment configuration for Soul Mirror.

## Server Details

- Provider: Vultr (https://my.vultr.com/)
- Location: Frankfurt
- IP: 45.76.89.58
- OS: Ubuntu
- Access: `ssh root@45.76.89.58`

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

**4. Open firewall**
```bash
ufw allow 80/tcp
ufw allow 443/tcp
ufw status
```

**5. Start services**
```bash
docker-compose up -d
```

**6. Verify**
```bash
docker-compose ps
docker-compose logs -f
curl http://45.76.89.58/api/status
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

## Future: Add Domain

**When domain ready (e.g., soulmirror.kira.dev):**

**1. Configure DNS at registrar**
- Add wildcard A record: `*.kira.dev` → `45.76.89.58`
- Wait 5-60 minutes for propagation

**2. Update nginx**
```bash
# Edit /etc/nginx/sites-available/soulmirror
# Change: server_name 45.76.89.58;
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
- `../apps/frontend-new/Dockerfile` - Frontend image
- `../scripts/deploy.sh` - Deploy script (runs on VPS)
- `../scripts/deploy-remote.sh` - Deploy script (runs locally, triggers VPS)
