# Infrastructure Configuration

VPS deployment configuration for Soul Mirror.

## Architecture

```
Internet (port 80)
    ↓
nginx (reverse proxy)
    ├─→ /api/* → localhost:8080 (backend container)
    └─→ /*     → localhost:3000 (frontend container)
```

## Components

**nginx**
- Listens on port 80 (public internet)
- Routes `/api/*` to backend service
- Routes everything else to frontend
- Supports WebSocket upgrades for hot reload

**Docker Compose**
- `backend` service: Python/FastAPI on port 8080
- `frontend` service: React/Vite on port 3000
- Both auto-restart on failure (`unless-stopped`)
- Backend reads `.env` from `apps/backend/.env`

## Deployment

**SSH Access**
```bash
ssh root@45.76.89.58
```

**1. Copy nginx config**
```bash
cp infra/nginx.conf /etc/nginx/sites-available/soulmirror
ln -s /etc/nginx/sites-available/soulmirror /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

**2. Open firewall ports**
```bash
ufw allow 80/tcp
ufw allow 443/tcp
ufw status
```

**3. Create backend environment**
```bash
cd apps/backend
cat > .env << 'EOF'
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
PORT=8080
ENVIRONMENT=production
EOF
cd ../..
```

**4. Start services**
```bash
docker-compose up -d
```

**5. Verify**
```bash
docker-compose ps
docker-compose logs -f
curl http://45.76.89.58/api/status
```

## Management

**View logs**
```bash
docker-compose logs backend
docker-compose logs frontend
docker-compose logs -f  # follow all
```

**Restart services**
```bash
docker-compose restart
docker-compose restart backend  # specific service
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

**Check if nginx is running and listening**
```bash
systemctl status nginx
ss -tlnp | grep ':80'
```

**Check firewall (common issue)**
```bash
ufw status
# If port 80/443 not allowed:
ufw allow 80/tcp
ufw allow 443/tcp
```

**Test connectivity**
```bash
# From server (should work):
curl http://localhost/api/status

# From outside (check if firewall blocks):
curl http://45.76.89.58/api/status -v
ping 45.76.89.58
```

## Files

- `nginx.conf` - Reverse proxy configuration
- `../docker-compose.yml` - Container orchestration
- `../apps/backend/Dockerfile` - Backend container image
- `../apps/frontend-new/Dockerfile` - Frontend container image

## Server Details

- Provider: Vultr
- Location: Frankfurt
- IP: 45.76.89.58
- OS: Ubuntu
- Access: SSH as root
