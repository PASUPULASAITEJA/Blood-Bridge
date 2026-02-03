# BloodBridge - AWS Deployment Guide

## ✅ Project Status: PRODUCTION READY

Your BloodBridge application is now fully prepared for AWS deployment!

---

## 📋 What's Included

### Core Application
- **`app_aws_integrated.py`** - Main Flask app with AWS DynamoDB & SNS integration
- **`config.py`** - Development, Production, and Testing configurations
- **`requirements.txt`** - All Python dependencies including boto3, gunicorn

### AWS Integration
- **`aws/dynamodb_helper.py`** - DynamoDB operations (CRUD for users, requests, inventory)
- **`aws/sns_helper.py`** - AWS SNS for SMS notifications
- **`aws/dynamodb_setup.py`** - Script to create DynamoDB tables
- **`aws/sns_setup.py`** - Script to create SNS topics

### Deployment Tools
- **`Procfile`** - Gunicorn configuration for production
- **`.env.example`** - Environment variables template
- **`setup_aws.sh`** - Local AWS setup automation
- **`deploy_ec2.sh`** - EC2 instance setup script
- **`AWS_DEPLOYMENT_CHECKLIST.md`** - Step-by-step deployment guide

---

## 🚀 Quick Start Deployment

### Option 1: Local Development (Recommended First)

```bash
# 1. Clone or navigate to project
cd BloodBridge

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run in development mode (no AWS needed)
set FLASK_ENV=development
set USE_AWS=false
python app_aws_integrated.py

# Access at http://127.0.0.1:5000
# Demo account: john@demo.com / demo123
```

### Option 2: AWS Deployment (Production)

#### Step 1: Prepare AWS

```bash
# 1. Configure AWS credentials
aws configure
# Enter: AWS Access Key ID, Secret Key, Region (us-east-1), Format (json)

# 2. Create DynamoDB tables
python aws/dynamodb_setup.py

# 3. Create SNS topics
python aws/sns_setup.py
# Note: Copy the Topic ARNs from output
```

#### Step 2: Configure Environment

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env file
# - Generate SECRET_KEY: python -c "import secrets; print(secrets.token_hex(32))"
# - Update SNS_ALERTS_TOPIC and SNS_EMERGENCY_TOPIC
# - Set USE_AWS=true
```

#### Step 3: Deploy to EC2

```bash
# 1. SSH to your EC2 instance
ssh -i your-key.pem ec2-user@your-instance-ip

# 2. Download and run deployment script
curl -O https://raw.githubusercontent.com/your-repo/deploy_ec2.sh
sudo bash deploy_ec2.sh

# 3. Configure environment
sudo nano /etc/bloodbridge/.env

# 4. Start service
sudo systemctl start bloodbridge
sudo systemctl enable bloodbridge  # Auto-start on reboot

# 5. Access your application
# http://your-instance-ip
```

---

## 📊 Architecture

```
┌─────────────────────────────────────────────────────┐
│                   FloodBridge App                   │
│         (app_aws_integrated.py - Hybrid Mode)       │
└─────────────────────────────────────────────────────┘
                           │
                           ├──► AWS DynamoDB (Users, Requests, Inventory)
                           ├──► AWS SNS (SMS Notifications)
                           └──► CloudWatch (Logging)
                           
Gunicorn Workers (4)
    │
    └──► Nginx Reverse Proxy (Port 80/443)
         └──► EC2 Instance
              └──► Load Balancer (Optional)
```

---

## 🔑 Environment Variables

**Required for Production:**
```
FLASK_ENV=production
SECRET_KEY=<strong-random-string>
USE_AWS=true
AWS_REGION=us-east-1
SNS_ALERTS_TOPIC=arn:aws:sns:us-east-1:ACCOUNT_ID:bloodbridge-alerts
SNS_EMERGENCY_TOPIC=arn:aws:sns:us-east-1:ACCOUNT_ID:bloodbridge-emergency
```

**Optional:**
```
DYNAMODB_USERS_TABLE=bloodbridge_users
DYNAMODB_REQUESTS_TABLE=bloodbridge_requests
DYNAMODB_INVENTORY_TABLE=bloodbridge_inventory
DYNAMODB_EMERGENCIES_TABLE=bloodbridge_emergencies
PORT=80
WORKERS=4
```

---

## 🧪 Testing Deployment

### Local Test (Before EC2)
```bash
set USE_AWS=false
python app_aws_integrated.py
# Should work without AWS credentials
```

### With AWS Services (Local)
```bash
set USE_AWS=true
set FLASK_ENV=development
python app_aws_integrated.py
# Requires AWS credentials configured
```

### On EC2
```bash
sudo systemctl status bloodbridge
sudo tail -f /var/log/bloodbridge/error.log
curl http://localhost:8000/  # Should return HTML
```

---

## 📱 Features Included

### User Management
- ✅ Registration with phone number
- ✅ Login/Logout
- ✅ User profiles with badges
- ✅ Donor leaderboard

### Blood Requests
- ✅ Create blood requests
- ✅ Find compatible donors
- ✅ Respond to requests
- ✅ Confirm donations
- ✅ Track donation history

### Notifications
- ✅ SMS to compatible donors
- ✅ SMS to requester when donor found
- ✅ Emergency SOS alerts
- ✅ Camp reminders

### Real-Time Features
- ✅ Live donor dashboard
- ✅ Blood inventory tracking
- ✅ Activity feed
- ✅ Online donor count

### Gamification
- ✅ Badge system (First Blood, Lifesaver, Hero, etc.)
- ✅ Leaderboard rankings
- ✅ Lives saved counter

---

## 🔒 Security Features

- ✅ Password hashing with Werkzeug
- ✅ Session management
- ✅ Environment-based secrets
- ✅ DynamoDB encryption
- ✅ HTTPS ready (with Let's Encrypt)
- ✅ SQL injection prevention (DynamoDB queries)
- ✅ CSRF protection in Flask
- ✅ Secure SNS communication

---

## 🛠️ Troubleshooting

### "DynamoDB table not found"
```bash
# Recreate tables
python aws/dynamodb_setup.py
```

### "SNS service unavailable"
- Application automatically falls back to local storage
- Check CloudWatch logs for SNS errors
- Verify SNS topics exist and are correct

### "SMS not sending"
- Verify SNS account is **not in sandbox** mode
- Check phone numbers are in E.164 format (+919876543210)
- Review SNS spending limit (default $1/month)

### "High latency on EC2"
- Check EC2 instance size (t2.micro minimum)
- Verify DynamoDB read/write capacity
- Monitor CloudWatch metrics

---

## 📈 Scaling

### For more traffic:
1. **Increase Gunicorn workers** in `/etc/bloodbridge/.env`
2. **Use Application Load Balancer** (ALB) for multiple EC2 instances
3. **Enable DynamoDB auto-scaling** for tables
4. **Add CloudFront** for static asset caching
5. **Use RDS** if moving away from DynamoDB

### Cost optimization:
- Use t2.micro EC2 (free tier eligible)
- DynamoDB on-demand pricing for variable load
- CloudWatch log retention: 7 days default
- Set SNS spending alerts

---

## 📚 Documentation

- **AWS_DEPLOYMENT_CHECKLIST.md** - Detailed step-by-step guide
- **setup_aws.sh** - Automated local AWS setup
- **deploy_ec2.sh** - Automated EC2 setup
- **config.py** - Configuration documentation
- **aws/dynamodb_helper.py** - Database operations documentation
- **aws/sns_helper.py** - Notification operations documentation

---

## ✨ What Makes This Production-Ready

1. ✅ **Hybrid Architecture** - Works with or without AWS
2. ✅ **Error Handling** - Automatic fallback to local storage
3. ✅ **Logging** - CloudWatch integration
4. ✅ **Security** - Environment-based secrets, no hardcoded credentials
5. ✅ **Scalability** - Gunicorn with multiple workers
6. ✅ **Monitoring** - Application and system logging
7. ✅ **Configuration** - Separate dev/prod configs
8. ✅ **Notifications** - Full SNS integration
9. ✅ **Persistence** - DynamoDB for data storage
10. ✅ **Deployment** - Systemd service, Nginx proxy

---

## 🎯 Next Steps

1. **Read** `AWS_DEPLOYMENT_CHECKLIST.md` for detailed instructions
2. **Test locally** with `USE_AWS=false`
3. **Configure AWS** services (DynamoDB, SNS)
4. **Launch EC2** instance
5. **Run deployment** scripts
6. **Monitor** with CloudWatch
7. **Celebrate** your deployment! 🎉

---

## 📞 Support

For issues or questions:
- Check logs: `/var/log/bloodbridge/error.log`
- Review CloudWatch metrics
- Check AWS service status
- Verify environment variables with `env | grep BLOOD`

---

## 📝 License

[Your License Here]

---

**BloodBridge is now ready for AWS production deployment! 🩸❤️**