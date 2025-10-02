# VPS Deployment Instructions

**Context:** This file guides deployment of Soul Mirror to a VPS. Follow these steps in order.

## Prerequisites

- Fresh Ubuntu VPS with root access
- Public IP address assigned
- Git installed (`apt install git -y`)

## Step 1: Install Dependencies

```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Install nginx
apt install nginx -y
```

## Step 2: Clone Repository

```bash
cd /root
git clone <REPO_URL> soul-mirror
cd soul-mirror
```

## Step 3: Configure Environment

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

## Step 4: Create Docker Compose

Create `/root/soul-mirror/docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./apps/backend
    ports:
      - "8080:8080"
    environment:
      - LLM_PROVIDER=anthropic
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - PORT=8080
    restart: unless-stopped

  frontend:
    build: ./apps/frontend-new
    ports:
      - "3000:3000"
    environment:
      - VITE_API_BASE=http://localhost:8080
    restart: unless-stopped
```

Create Dockerfiles if needed:
- `apps/backend/Dockerfile`
- `apps/frontend-new/Dockerfile`

## Step 5: Configure Nginx

Create `/etc/nginx/sites-available/soulmirror`:

```nginx
server {
    listen 80;
    server_name <IP_ADDRESS>;

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

## Step 6: Start Services

```bash
cd /root/soul-mirror
docker-compose up -d
```

## Step 7: Verify

- Check containers: `docker-compose ps`
- Check logs: `docker-compose logs -f`
- Visit `http://<IP_ADDRESS>` in browser

## Future: Add Domain

When domain is ready:
1. Add DNS: `*.yourdomain.dev` → VPS IP
2. Update nginx `server_name` from IP to `soulmirror.yourdomain.dev`
3. Add SSL with certbot: `apt install certbot python3-certbot-nginx -y && certbot --nginx`

## Troubleshooting

- Check nginx: `systemctl status nginx`
- Check containers: `docker-compose logs`
- Restart: `docker-compose restart`
- Rebuild: `docker-compose up -d --build`
