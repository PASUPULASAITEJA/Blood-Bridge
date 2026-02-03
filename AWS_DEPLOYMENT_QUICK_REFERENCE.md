# BloodBridge - AWS Deployment Quick Reference

## 🚀 Quick Command Reference

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in dev mode (no AWS needed)
set FLASK_ENV=development
set USE_AWS=false
python app_aws_integrated.py

# Access at http://127.0.0.1:5000
# Demo: john@demo.com / demo123
```

### AWS Configuration

```bash
# Configure AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region (us-east-1), Format (json)

# Verify credentials
aws sts get-caller-identity

# List configured profiles
aws configure list
```

### AWS Service Setup

```bash
# Create DynamoDB tables
python aws/dynamodb_setup.py

# Create SNS topics
python aws/sns_setup.py

# List DynamoDB tables
aws dynamodb list-tables --region us-east-1

# List SNS topics
aws sns list-topics --region us-east-1

# Get SNS topic attributes
aws sns get-topic-attributes --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:bloodbridge-alerts --region us-east-1
```

### Environment Management

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Copy environment template
cp .env.example .env

# Edit environment (Linux/Mac)
nano .env

# Edit environment (Windows)
notepad .env

# Load environment (Linux/Mac)
export $(cat .env | xargs)

# Check environment variables
env | grep BLOOD

# View specific variable
echo $SECRET_KEY
```

### EC2 Deployment

```bash
# SSH to EC2 instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Copy deployment script
scp -i your-key.pem deploy_ec2.sh ec2-user@your-instance-ip:~

# Run deployment on EC2
ssh -i your-key.pem ec2-user@your-instance-ip 'sudo bash ~/deploy_ec2.sh'
```

### Service Management (on EC2)

```bash
# Start BloodBridge service
sudo systemctl start bloodbridge

# Stop service
sudo systemctl stop bloodbridge

# Restart service
sudo systemctl restart bloodbridge

# Check service status
sudo systemctl status bloodbridge

# Enable auto-start on reboot
sudo systemctl enable bloodbridge

# Disable auto-start
sudo systemctl disable bloodbridge

# View service logs
sudo journalctl -u bloodbridge -f  # Real-time
sudo journalctl -u bloodbridge -n 50  # Last 50 lines
```

### Nginx Management

```bash
# Start Nginx
sudo systemctl start nginx

# Stop Nginx
sudo systemctl stop nginx

# Reload configuration
sudo nginx -s reload
sudo systemctl reload nginx

# Test configuration
sudo nginx -t

# View Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Application Logs

```bash
# Application error log
sudo tail -f /var/log/bloodbridge/error.log

# Application access log
sudo tail -f /var/log/bloodbridge/access.log

# Both logs together
sudo tail -f /var/log/bloodbridge/*.log

# Last 100 lines of error log
sudo tail -100 /var/log/bloodbridge/error.log

# Search logs for errors
sudo grep ERROR /var/log/bloodbridge/error.log

# Real-time monitoring
watch -n 1 'tail -10 /var/log/bloodbridge/error.log'
```

### AWS CLI - Monitoring

```bash
# CloudWatch - Get recent logs
aws logs tail /aws/bloodbridge/app --follow

# CloudWatch - Get specific time range
aws logs tail /aws/bloodbridge/app --since 1h

# Get EC2 instance details
aws ec2 describe-instances --region us-east-1

# Get EC2 instance status
aws ec2 describe-instance-status --region us-east-1

# Get EC2 CPU utilization
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --dimensions Name=InstanceId,Value=i-xxxxxx \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-01T23:59:59Z \
  --period 300 \
  --statistics Average
```

### DynamoDB Operations

```bash
# Scan table
aws dynamodb scan --table-name bloodbridge_users --region us-east-1

# Get item
aws dynamodb get-item \
  --table-name bloodbridge_users \
  --key '{"user_id":{"S":"uuid-here"}}' \
  --region us-east-1

# Put item
aws dynamodb put-item \
  --table-name bloodbridge_users \
  --item file://item.json \
  --region us-east-1

# Delete table (warning!)
aws dynamodb delete-table --table-name bloodbridge_users --region us-east-1

# Describe table
aws dynamodb describe-table --table-name bloodbridge_users --region us-east-1
```

### SNS Operations

```bash
# Publish message to topic
aws sns publish \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:bloodbridge-alerts \
  --subject "Test Subject" \
  --message "Test message" \
  --region us-east-1

# Publish SMS
aws sns publish \
  --phone-number +919876543210 \
  --message "Hello from BloodBridge!" \
  --region us-east-1

# List topic subscriptions
aws sns list-subscriptions-by-topic \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:bloodbridge-alerts \
  --region us-east-1

# Get topic attributes
aws sns get-topic-attributes \
  --topic-arn arn:aws:sns:us-east-1:ACCOUNT_ID:bloodbridge-alerts \
  --region us-east-1
```

### EC2 Instance Management

```bash
# Start instance
aws ec2 start-instances --instance-ids i-xxxxxx --region us-east-1

# Stop instance
aws ec2 stop-instances --instance-ids i-xxxxxx --region us-east-1

# Terminate instance (WARNING - deletes everything!)
aws ec2 terminate-instances --instance-ids i-xxxxxx --region us-east-1

# Get instance public IP
aws ec2 describe-instances \
  --instance-ids i-xxxxxx \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --region us-east-1
```

### IAM Permissions

```bash
# Create IAM policy for BloodBridge
aws iam create-policy \
  --policy-name BloodBridgePolicy \
  --policy-document file://iam_policy.json

# Attach policy to user
aws iam attach-user-policy \
  --user-name bloodbridge-user \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/BloodBridgePolicy

# List user policies
aws iam list-user-policies --user-name bloodbridge-user

# List attached policies
aws iam list-attached-user-policies --user-name bloodbridge-user
```

### Troubleshooting Commands

```bash
# Check port 80 is listening
sudo netstat -tuln | grep :80
sudo ss -tuln | grep :80

# Check if service is running
ps aux | grep gunicorn

# Check available disk space
df -h

# Check available memory
free -h

# Check system uptime
uptime

# Test network connectivity to AWS
ping dynamodb.us-east-1.amazonaws.com

# Test DNS resolution
nslookup sns.us-east-1.amazonaws.com

# Check application is responding
curl -I http://127.0.0.1:8000/health

# Reload environment variables
source ~/.bashrc
source ~/.profile
```

### Testing Application

```bash
# Test with curl (check service is running)
curl http://localhost:8000/
curl http://localhost:8000/api/blood-facts

# Load testing (using Apache Bench)
ab -n 100 -c 10 http://your-ip/

# Monitor performance during test
watch -n 1 'ps aux | grep gunicorn'
```

### Backup & Recovery

```bash
# Create DynamoDB backup
aws dynamodb create-backup \
  --table-name bloodbridge_users \
  --backup-name bloodbridge-users-backup-$(date +%Y%m%d-%H%M%S) \
  --region us-east-1

# List backups
aws dynamodb list-backups --region us-east-1

# Restore from backup
aws dynamodb restore-table-from-backup \
  --target-table-name bloodbridge_users_restored \
  --backup-arn arn:aws:dynamodb:us-east-1:ACCOUNT_ID:table/bloodbridge_users/backup/... \
  --region us-east-1

# Backup logs
aws logs create-export-task \
  --log-group-name /aws/bloodbridge/app \
  --from 1000000000000 \
  --to 2000000000000 \
  --destination my-s3-bucket \
  --destination-prefix bloodbridge-logs
```

### Useful One-Liners

```bash
# Get instance IP and connect immediately
ssh -i key.pem ec2-user@$(aws ec2 describe-instances \
  --filters 'Name=instance-state-name,Values=running' \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text --region us-east-1)

# Tail logs with timestamps
sudo tail -f /var/log/bloodbridge/error.log | sed 's/^/[$(date)] /'

# Count requests per hour
sudo awk '{print $4}' /var/log/bloodbridge/access.log | cut -d: -f1 | uniq -c

# Check service restart count
sudo systemctl status bloodbridge | grep "Active:"

# Monitor system resources
watch -n 1 "free -h && echo && df -h"
```

---

## 📊 Useful Dashboards

### CloudWatch Console
```
AWS Console → CloudWatch → Log Groups → /aws/bloodbridge/app
```

### EC2 Monitoring
```
AWS Console → EC2 → Instances → Select Instance → Monitoring Tab
```

### DynamoDB Console
```
AWS Console → DynamoDB → Tables → Select Table → Monitoring
```

### SNS Console
```
AWS Console → SNS → Topics → Select Topic → Monitor with CloudWatch
```

---

## ⚠️ Dangerous Commands (Use with Caution)

```bash
# Delete entire DynamoDB table (no recovery!)
aws dynamodb delete-table --table-name bloodbridge_users

# Terminate EC2 instance (deletes all data!)
aws ec2 terminate-instances --instance-ids i-xxxxx

# Empty all logs (no recovery!)
sudo rm -rf /var/log/bloodbridge/*

# Restart service in production (causes downtime!)
sudo systemctl restart bloodbridge
```

---

## 🎯 Common Workflows

### Deploy New Version
```bash
# 1. SSH to EC2
ssh -i key.pem ec2-user@instance-ip

# 2. Pull latest code
cd ~/bloodbridge && git pull

# 3. Install new dependencies (if any)
source venv/bin/activate
pip install -r requirements.txt

# 4. Restart service (short downtime)
sudo systemctl restart bloodbridge

# 5. Check status
sudo systemctl status bloodbridge
```

### Debug Application Issue
```bash
# 1. Check service status
sudo systemctl status bloodbridge

# 2. View error logs
sudo tail -100 /var/log/bloodbridge/error.log | less

# 3. Check AWS connectivity
aws dynamodb list-tables --region us-east-1

# 4. Test endpoint
curl -v http://localhost:8000/

# 5. Check system resources
free -h && df -h
```

### Emergency Rollback
```bash
# 1. SSH to EC2
ssh -i key.pem ec2-user@instance-ip

# 2. Go to previous version
cd ~/bloodbridge
git revert HEAD

# 3. Reinstall if needed
pip install -r requirements.txt

# 4. Restart
sudo systemctl restart bloodbridge
```

---

**Keep this file handy for quick reference during deployment and operations!** 📋
