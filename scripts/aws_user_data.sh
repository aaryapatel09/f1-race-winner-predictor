#!/bin/bash

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.5.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create application directory
mkdir -p /app
cd /app

# Clone repository (replace with your repository URL)
git clone https://github.com/yourusername/f1-predictor.git .

# Set up environment variables
cat > .env << EOL
CLOUD_PROVIDER=aws
PROJECT_ID=${PROJECT_ID}
REGION=${REGION}
INSTANCE_TYPE=${INSTANCE_TYPE}
EOL

# Build and run the application
docker-compose up -d --build

# Set up monitoring
apt-get install -y prometheus node-exporter
systemctl enable prometheus node-exporter
systemctl start prometheus node-exporter

# Set up logging
mkdir -p /var/log/f1-predictor
chmod 755 /var/log/f1-predictor

# Create logrotate configuration
cat > /etc/logrotate.d/f1-predictor << EOL
/var/log/f1-predictor/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOL

# Set up basic security
ufw allow 22
ufw allow 80
ufw allow 443
ufw --force enable

# Install fail2ban
apt-get install -y fail2ban
systemctl enable fail2ban
systemctl start fail2ban

# Create monitoring dashboard
cat > /app/monitoring/dashboard.json << EOL
{
  "dashboard": {
    "id": null,
    "title": "F1 Predictor Dashboard",
    "tags": ["f1", "predictor"],
    "timezone": "browser",
    "panels": [
      {
        "title": "CPU Usage",
        "type": "graph",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "node_cpu_seconds_total{mode='idle'}",
            "legendFormat": "CPU Usage"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "datasource": "Prometheus",
        "targets": [
          {
            "expr": "node_memory_MemTotal_bytes - node_memory_MemFree_bytes",
            "legendFormat": "Memory Usage"
          }
        ]
      }
    ]
  }
}
EOL

# Set up automatic updates
cat > /etc/systemd/system/update-f1-predictor.service << EOL
[Unit]
Description=Update F1 Predictor Application
After=network.target

[Service]
Type=oneshot
WorkingDirectory=/app
ExecStart=/usr/bin/git pull
ExecStart=/usr/local/bin/docker-compose up -d --build
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOL

systemctl enable update-f1-predictor
systemctl start update-f1-predictor

# Create a cron job for daily updates
echo "0 0 * * * /usr/bin/systemctl start update-f1-predictor" | crontab -

# Set up backup
apt-get install -y awscli
mkdir -p /backup

cat > /etc/systemd/system/backup-f1-predictor.service << EOL
[Unit]
Description=Backup F1 Predictor Data
After=network.target

[Service]
Type=oneshot
WorkingDirectory=/app
ExecStart=/usr/bin/tar -czf /backup/f1-predictor-\$(date +%%Y%%m%%d).tar.gz data/
ExecStart=/usr/bin/aws s3 cp /backup/f1-predictor-\$(date +%%Y%%m%%d).tar.gz s3://your-backup-bucket/
ExecStart=/usr/bin/find /backup -type f -mtime +7 -delete
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOL

systemctl enable backup-f1-predictor
systemctl start backup-f1-predictor

# Create a cron job for weekly backups
echo "0 1 * * 0 /usr/bin/systemctl start backup-f1-predictor" | crontab -

# Final system update and cleanup
apt-get update
apt-get upgrade -y
apt-get autoremove -y
apt-get clean

# Reboot to apply all changes
reboot 