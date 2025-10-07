# Domain Setup Guide

Guide for pointing kiraistaken.lol to your VPS.

## Step 1: Get Your VPS IP Address

Find your VPS IP address:
```bash
# SSH into your VPS and run:
curl ifconfig.me
```

Or check your VPS provider's dashboard.

## Step 2: Configure DNS in Namecheap

1. Go to Namecheap dashboard → Domain List
2. Click "Manage" next to kiraistaken.lol
3. Click on "Advanced DNS" tab
4. Add/modify these DNS records:

### Required Records

**A Record (for root domain):**
- Type: `A Record`
- Host: `@`
- Value: `YOUR_VPS_IP_ADDRESS`
- TTL: `Automatic` or `300`

**A Record (for www subdomain):**
- Type: `A Record`
- Host: `www`
- Value: `YOUR_VPS_IP_ADDRESS`
- TTL: `Automatic` or `300`

### Optional: Wildcard Subdomain

If you want all subdomains to point to your VPS:
- Type: `A Record`
- Host: `*`
- Value: `YOUR_VPS_IP_ADDRESS`
- TTL: `Automatic` or `300`

## Step 3: Remove Conflicting Records

Delete any existing records that might conflict:
- Remove URL redirect records (shown in your screenshot)
- Remove CNAME records for `@` or `www` if present
- Keep only nameserver records and the A records you just created

## Step 4: Wait for DNS Propagation

DNS changes take time to propagate:
- Namecheap: 30 minutes to 2 hours typically
- Full global propagation: up to 48 hours

Check propagation status:
```bash
# Check if DNS is resolving
dig kiraistaken.lol
dig www.kiraistaken.lol

# Or use online tools
# https://dnschecker.org
```

## Step 5: Configure Nginx on VPS

Update nginx configuration to handle the new domain:

```bash
# SSH into VPS
ssh user@YOUR_VPS_IP

# Edit nginx config
sudo nano /etc/nginx/sites-available/soul-mirror

# Add kiraistaken.lol to server_name
server {
    listen 80;
    server_name kiraistaken.lol www.kiraistaken.lol;
    # ... rest of config
}

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

## Step 6: Setup SSL Certificate

Once DNS is working, add HTTPS:

```bash
# Install certbot if not already installed
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d kiraistaken.lol -d www.kiraistaken.lol

# Certificate auto-renewal is configured automatically
```

## Verification

Test your setup:

```bash
# HTTP access
curl -I http://kiraistaken.lol

# HTTPS access (after SSL setup)
curl -I https://kiraistaken.lol

# Check certificate
curl -vI https://kiraistaken.lol 2>&1 | grep -i "SSL certificate"
```

## Troubleshooting

**DNS not resolving:**
- Wait longer (up to 48h)
- Clear local DNS cache: `sudo dscacheutil -flushcache` (macOS)
- Check DNS propagation at dnschecker.org

**Nginx not responding:**
- Check nginx status: `sudo systemctl status nginx`
- Check logs: `sudo tail -f /var/log/nginx/error.log`
- Verify VPS firewall allows ports 80/443

**SSL certificate fails:**
- Ensure DNS is fully propagated first
- Check if port 80 is accessible from internet
- Verify nginx config is correct
