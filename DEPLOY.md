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

**What:** Create environment variables for the backend service.

**Why:** Backend needs API keys to connect to LLM provider (Anthropic/OpenAI) and configuration for production mode.

**How:**
```bash
cd apps/backend
cat > .env << 'EOF'
LLM_PROVIDER=anthropic          # Use Anthropic's Claude (can also be "openai")
ANTHROPIC_API_KEY=<YOUR_API_KEY> # Your Anthropic API key from console.anthropic.com
PORT=8080                        # Backend server port (must match docker-compose)
ENVIRONMENT=production           # Production mode (vs development)
EOF
cd ../..
```

**Note:** Replace `<YOUR_API_KEY>` with actual API key before running.

## Step 2: Configure Nginx

**What:** Set up nginx as reverse proxy to route incoming HTTP traffic to Docker containers.

**Why:**
- Nginx handles external HTTP requests on port 80 (standard web port)
- Routes `/api/*` requests to backend container (port 8080)
- Routes all other requests to frontend container (port 3000)
- Single entry point for the entire application

**How:**
```bash
cat > /etc/nginx/sites-available/soulmirror << 'EOF'
server {
    listen 80;                    # Listen on port 80 (HTTP)
    server_name 45.76.89.58;      # Respond to requests for this IP

    # Backend API routes (anything starting with /api)
    location /api {
        proxy_pass http://localhost:8080;      # Forward to backend container
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;    # Support WebSocket upgrades
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;               # Preserve original host
        proxy_cache_bypass $http_upgrade;
    }

    # Frontend routes (everything else)
    location / {
        proxy_pass http://localhost:3000;      # Forward to frontend container
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;    # Support hot reload in dev
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF
```

**Enable configuration:**
```bash
ln -s /etc/nginx/sites-available/soulmirror /etc/nginx/sites-enabled/  # Enable site
nginx -t                                                                # Test config syntax
systemctl reload nginx                                                  # Apply changes
```

## Step 3: Start Services

**What:** Build and start Docker containers for backend and frontend.

**Why:** Docker Compose orchestrates both services together with proper configuration.

**How:**
```bash
cd /root/soul-mirror
docker-compose up -d    # -d = detached mode (runs in background)
```

**What happens:**
1. Docker reads `docker-compose.yml`
2. Builds backend image from `apps/backend/Dockerfile`
3. Builds frontend image from `apps/frontend-new/Dockerfile`
4. Starts backend container on port 8080
5. Starts frontend container on port 3000
6. Both containers restart automatically if they crash (`restart: unless-stopped`)

## Step 4: Verify

**What:** Confirm everything is running correctly.

**How:**
```bash
# Check container status (should show both backend and frontend as "Up")
docker-compose ps

# Check logs (Ctrl+C to exit)
docker-compose logs -f

# Check specific service logs
docker-compose logs backend
docker-compose logs frontend
```

**Test in browser:**
- Visit http://45.76.89.58 → Should load Soul Mirror frontend
- Backend API: http://45.76.89.58/api/status → Should return JSON status

**Expected flow:**
1. Browser requests http://45.76.89.58
2. Nginx receives request on port 80
3. Nginx forwards to frontend container (port 3000)
4. Frontend makes API calls to `/api/*`
5. Nginx forwards API calls to backend container (port 8080)
6. Backend processes with LangChain/LangGraph

## Future: Add Domain

**What:** Replace IP address with custom domain name and add HTTPS.

**When domain is ready (e.g., kira.dev):**

**Step 1: Configure DNS at domain registrar**
- Add wildcard A record: `*.kira.dev` → `45.76.89.58`
- This allows any subdomain (soulmirror.kira.dev, resume.kira.dev, etc.) to point to VPS
- DNS propagation takes 5-60 minutes

**Step 2: Update nginx configuration**
```bash
# Edit /etc/nginx/sites-available/soulmirror
# Change: server_name 45.76.89.58;
# To:     server_name soulmirror.kira.dev;
systemctl reload nginx
```

**Step 3: Add SSL certificate (HTTPS)**
```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx  # Follow prompts, select soulmirror.kira.dev
```

**Result:**
- Access via https://soulmirror.kira.dev (encrypted)
- Auto-renewal of SSL certificate every 90 days
- HTTP automatically redirects to HTTPS

## Troubleshooting

**Nginx issues:**
```bash
systemctl status nginx          # Check if nginx is running
nginx -t                        # Test configuration for syntax errors
systemctl restart nginx         # Restart nginx
journalctl -u nginx -f         # View nginx system logs
```

**Docker container issues:**
```bash
docker-compose ps               # Check which containers are running
docker-compose logs backend     # View backend logs
docker-compose logs frontend    # View frontend logs
docker-compose restart          # Restart all containers
docker-compose restart backend  # Restart specific container
docker-compose down             # Stop all containers
docker-compose up -d --build    # Rebuild and restart (use after code changes)
```

**Common issues:**
- **Port already in use:** Check with `netstat -tlnp | grep :8080` or `:3000`
- **Container won't start:** Check logs with `docker-compose logs`
- **API not responding:** Verify backend container is running and `.env` has API key
- **Can't access from browser:** Check firewall allows port 80: `ufw status`
- **Changes not showing:** Rebuild containers: `docker-compose up -d --build`
