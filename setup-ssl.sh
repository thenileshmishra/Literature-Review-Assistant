#!/bin/bash
# SSL Setup Script for agent.nileshmishra.info
# Run this ONCE on EC2 after DNS is pointed to the instance

set -e

echo "=========================================="
echo "SSL Setup for agent.nileshmishra.info"
echo "=========================================="

# Check if DNS is resolving
echo "Checking DNS resolution..."
IP=$(dig +short agent.nileshmishra.info | tail -n1)
if [ -z "$IP" ]; then
    echo "❌ ERROR: DNS not resolving for agent.nileshmishra.info"
    echo "Please set up DNS A record first, then wait 5-10 minutes"
    exit 1
fi

echo "✅ DNS resolves to: $IP"
echo ""

# Install Certbot
echo "Installing Certbot..."
sudo dnf install -y certbot

# Create webroot directory
echo "Creating certbot webroot directory..."
sudo mkdir -p /var/www/certbot
sudo chmod -R 755 /var/www/certbot

# Stop existing containers
echo "Stopping existing containers..."
docker stop nginx frontend backend 2>/dev/null || true
docker rm nginx frontend backend 2>/dev/null || true

# Start temporary nginx for certificate validation
echo "Starting temporary nginx for ACME challenge..."
docker run -d --name nginx-temp \
  -p 80:80 \
  -v /var/www/certbot:/var/www/certbot:ro \
  -v ~/nginx-temp.conf:/etc/nginx/conf.d/default.conf:ro \
  nginx:alpine

# Create temporary nginx config for ACME challenge
cat > ~/nginx-temp.conf <<'EOF'
server {
    listen 80;
    server_name agent.nileshmishra.info;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 200 "Certificate validation in progress...\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Reload nginx
docker exec nginx-temp nginx -s reload 2>/dev/null || docker restart nginx-temp

echo ""
echo "Requesting SSL certificate from Let's Encrypt..."
echo "This may take a minute..."
echo ""

# Request certificate
sudo certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email \
  -d agent.nileshmishra.info

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SSL Certificate obtained successfully!"
    echo ""
    
    # Stop temporary nginx
    docker stop nginx-temp
    docker rm nginx-temp
    
    # Set up certificate renewal
    echo "Setting up automatic certificate renewal..."
    sudo systemctl enable --now certbot-renew.timer 2>/dev/null || \
    (sudo crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet && docker restart nginx") | sudo crontab -
    
    echo ""
    echo "=========================================="
    echo "✅ SSL Setup Complete!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Push your code to GitHub to trigger deployment"
    echo "2. Access your app at: https://agent.nileshmishra.info"
    echo ""
    echo "Certificate will auto-renew every 60 days"
    echo "=========================================="
else
    echo ""
    echo "❌ Certificate request failed"
    echo "Please check:"
    echo "  1. DNS is properly pointed to this server"
    echo "  2. Port 80 is open in security group"
    echo "  3. Domain is accessible from internet"
    exit 1
fi
