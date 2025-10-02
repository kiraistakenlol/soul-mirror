# VPS Deployment Instructions

**Context:** This file guides deployment of Soul Mirror to a VPS. Follow these steps in order.

## Server Details

- Provider: Vultr (https://my.vultr.com/)
- Location: Frankfurt
- Public IP: 45.76.89.58
- OS: Ubuntu
- Access: SSH as root

## Prerequisites

- Repository already cloned to `/root/soul-mirror`
- `bootstrap.sh` already executed (installs Docker, nginx, Claude Code)
- Public IP address: 45.76.89.58

## Step 1: Configure Environment

Create `.env` files for backend:

```bash
# apps/backend/.env
cd apps/backend
cat > .env << 'EOF'
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=<YOUR_API_KEY>
PORT=8080
ENVIRONMENT=production
EOF
cd ../..
```

## Step 2: Configure Nginx

Create `/etc/nginx/sites-available/soulmirror`:

```nginx
server {
    listen 80;
    server_name 45.76.89.58;

    location /api {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable:
```bash
ln -s /etc/nginx/sites-available/soulmirror /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

## Step 3: Start Services

```bash
cd /root/soul-mirror
docker-compose up -d
```

## Step 4: Verify

- Check containers: `docker-compose ps`
- Check logs: `docker-compose logs -f`
- Visit http://45.76.89.58 in browser

## Future: Add Domain

When domain is ready (e.g., kira.dev):
1. Add DNS: `*.kira.dev` → 45.76.89.58
2. Update nginx `server_name` from IP to `soulmirror.kira.dev`
3. Add SSL with certbot: `apt install certbot python3-certbot-nginx -y && certbot --nginx`

## Troubleshooting

- Check nginx: `systemctl status nginx`
- Check containers: `docker-compose logs`
- Restart: `docker-compose restart`
- Rebuild: `docker-compose up -d --build`
