# Cloud Setup Guide

This guide explains how to deploy the F1 Race Winner Predictor to various cloud platforms.

## AWS Deployment

### EC2 Setup

1. Create an EC2 instance:
   - Choose Ubuntu Server 20.04 LTS
   - Select t2.micro for free tier or t2.small/medium for better performance
   - Configure security group to allow HTTP (port 80) and HTTPS (port 443)

2. Connect to your instance:
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

3. Install dependencies:
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-venv nginx
```

4. Clone the repository:
```bash
git clone https://github.com/aaryapatel09/f1-race-winner-predictor.git
cd f1-race-winner-predictor
```

5. Set up the application:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

6. Create a systemd service:
```bash
sudo nano /etc/systemd/system/f1predictor.service
```

Add the following content:
```ini
[Unit]
Description=F1 Race Winner Predictor
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/f1-race-winner-predictor
Environment="PATH=/home/ubuntu/f1-race-winner-predictor/venv/bin"
ExecStart=/home/ubuntu/f1-race-winner-predictor/venv/bin/streamlit run src/web/app.py

[Install]
WantedBy=multi-user.target
```

7. Start the service:
```bash
sudo systemctl start f1predictor
sudo systemctl enable f1predictor
```

### S3 Setup (for static files)

1. Create an S3 bucket:
   - Go to AWS S3 console
   - Click "Create bucket"
   - Configure bucket settings and permissions

2. Upload static files:
```bash
aws s3 sync static/ s3://your-bucket-name/static/
```

### CloudWatch Setup (for monitoring)

1. Create a CloudWatch dashboard:
   - Go to CloudWatch console
   - Click "Create dashboard"
   - Add relevant metrics (CPU, Memory, Network)

2. Set up alarms:
   - Configure alerts for high resource usage
   - Set up notification via SNS

## Google Cloud Platform Deployment

### Setup

1. Create a new project in GCP Console

2. Enable required APIs:
   - Compute Engine API
   - Cloud Build API
   - Container Registry API

3. Install Google Cloud SDK

### Deploy using App Engine

1. Create app.yaml:
```yaml
runtime: python39
entrypoint: streamlit run src/web/app.py --server.port=$PORT

instance_class: F1

automatic_scaling:
  target_cpu_utilization: 0.65
  min_instances: 1
  max_instances: 10
```

2. Deploy:
```bash
gcloud app deploy
```

### Deploy using Cloud Run

1. Create Dockerfile:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "src/web/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. Build and deploy:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/f1predictor
gcloud run deploy --image gcr.io/PROJECT_ID/f1predictor --platform managed
```

## Monitoring and Scaling

### AWS

- Use CloudWatch metrics to monitor application performance
- Set up Auto Scaling groups for EC2 instances
- Configure load balancer for high availability

### GCP

- Use Cloud Monitoring for performance tracking
- Enable auto-scaling in App Engine or Cloud Run
- Set up Cloud Load Balancing for traffic distribution

## Security Considerations

1. Use HTTPS for all traffic
2. Implement proper IAM roles and permissions
3. Regular security updates and patches
4. Secure storage of sensitive data using environment variables
5. Regular backups of application data

## Cost Management

1. Use free tier resources when possible
2. Monitor resource usage and costs
3. Set up billing alerts
4. Scale down resources during low-traffic periods

## Troubleshooting

1. Check application logs:
   - AWS: CloudWatch Logs
   - GCP: Cloud Logging

2. Monitor resource usage:
   - CPU utilization
   - Memory usage
   - Network traffic

3. Common issues:
   - Connection timeouts
   - Memory limits
   - CPU constraints 