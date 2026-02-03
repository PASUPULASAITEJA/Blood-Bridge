#!/bin/bash
# BloodBridge - EC2 Deployment Script
# Run this script on your EC2 instance after SSH

set -e

echo "╔════════════════════════════════════════════════════╗"
echo "║  BloodBridge - EC2 Deployment Script              ║"
echo "║  Run as: bash deploy_ec2.sh                       ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root (use sudo)"
   exit 1
fi

# Update system
echo "🔄 Updating system packages..."
yum update -y > /dev/null
echo "✅ System updated"
echo ""

# Install Python and dependencies
echo "📦 Installing Python and dependencies..."
yum install -y python3 python3-pip python3-venv git -y > /dev/null
echo "✅ Python installed"
echo ""

# Install Nginx (optional, for reverse proxy)
echo "🌐 Installing Nginx..."
amazon-linux-extras install nginx1 -y > /dev/null
systemctl enable nginx
systemctl start nginx
echo "✅ Nginx installed and running"
echo ""

# Clone repository
APP_DIR="/home/ec2-user/bloodbridge"
if [ ! -d "$APP_DIR" ]; then
    echo "📥 Cloning BloodBridge repository..."
    mkdir -p /home/ec2-user
    cd /home/ec2-user
    
    # Update the URL below to your actual repository
    echo "Enter your Git repository URL (or press Enter to skip):"
    read REPO_URL
    
    if [ ! -z "$REPO_URL" ]; then
        git clone "$REPO_URL" bloodbridge
    else
        echo "⚠️  Skipping Git clone. Upload files manually."
        mkdir -p bloodbridge
    fi
    
    chown -R ec2-user:ec2-user "$APP_DIR"
fi

echo "✅ App directory ready at $APP_DIR"
echo ""

# Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
cd "$APP_DIR"
python3 -m venv venv
source venv/bin/activate
echo "✅ Virtual environment created"
echo ""

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --quiet -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create log directory
echo "📝 Setting up logging..."
mkdir -p /var/log/bloodbridge
chown ec2-user:ec2-user /var/log/bloodbridge
touch /var/log/bloodbridge/access.log
touch /var/log/bloodbridge/error.log
echo "✅ Log directory created"
echo ""

# Create config directory for environment variables
echo "⚙️  Setting up environment..."
mkdir -p /etc/bloodbridge
touch /etc/bloodbridge/.env
chown ec2-user:ec2-user /etc/bloodbridge/.env
chmod 600 /etc/bloodbridge/.env

echo ""
echo "⚠️  IMPORTANT: Edit the environment file"
echo "   Location: /etc/bloodbridge/.env"
echo ""
echo "   Required variables:"
echo "   - FLASK_ENV=production"
echo "   - SECRET_KEY=<generate with: python -c 'import secrets; print(secrets.token_hex(32))'>"
echo "   - AWS_REGION=us-east-1"
echo "   - SNS_ALERTS_TOPIC=arn:aws:sns:..."
echo "   - SNS_EMERGENCY_TOPIC=arn:aws:sns:..."
echo "   - USE_AWS=true"
echo ""
echo "Run: sudo nano /etc/bloodbridge/.env"
echo ""

# Create systemd service
echo "🚀 Creating systemd service..."
cat > /etc/systemd/system/bloodbridge.service << 'EOF'
[Unit]
Description=BloodBridge Blood Bank Application
After=network.target

[Service]
Type=notify
User=ec2-user
WorkingDirectory=/home/ec2-user/bloodbridge
ExecStart=/home/ec2-user/bloodbridge/venv/bin/gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class sync \
    --timeout 30 \
    --access-logfile /var/log/bloodbridge/access.log \
    --error-logfile /var/log/bloodbridge/error.log \
    app_aws_integrated:app

Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Environment variables
EnvironmentFile=/etc/bloodbridge/.env

[Install]
WantedBy=multi-user.target
EOF

chmod 644 /etc/systemd/system/bloodbridge.service
systemctl daemon-reload
echo "✅ Systemd service created"
echo ""

# Create Nginx configuration
echo "🌐 Configuring Nginx reverse proxy..."
cat > /etc/nginx/conf.d/bloodbridge.conf << 'EOF'
upstream bloodbridge {
    server 127.0.0.1:8000;
}

server {
    listen 80 default_server;
    listen [::]:80 default_server;
    
    server_name _;
    client_max_body_size 10M;
    
    # Logging
    access_log /var/log/nginx/bloodbridge_access.log;
    error_log /var/log/nginx/bloodbridge_error.log;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css text/javascript application/json;
    
    location / {
        proxy_pass http://bloodbridge;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files (if needed)
    location /static {
        alias /home/ec2-user/bloodbridge/templates;
        expires 30d;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

systemctl reload nginx
echo "✅ Nginx configured as reverse proxy"
echo ""

echo "╔════════════════════════════════════════════════════╗"
echo "║  ✅ EC2 Setup Complete!                           ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "1️⃣  Configure environment:"
echo "    sudo nano /etc/bloodbridge/.env"
echo ""
echo "2️⃣  Start the application:"
echo "    sudo systemctl start bloodbridge"
echo "    sudo systemctl status bloodbridge"
echo ""
echo "3️⃣  Check logs:"
echo "    sudo tail -f /var/log/bloodbridge/error.log"
echo "    sudo tail -f /var/log/bloodbridge/access.log"
echo ""
echo "4️⃣  (Optional) Set up HTTPS with Let's Encrypt:"
echo "    sudo yum install certbot python3-certbot-nginx -y"
echo "    sudo certbot certonly --standalone -d yourdomain.com"
echo ""
echo "5️⃣  Enable auto-start on reboot:"
echo "    sudo systemctl enable bloodbridge"
echo ""
echo "Application URL: http://$(hostname -I | awk '{print $1}')"
echo ""
