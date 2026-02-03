# BloodBridge - AWS Deployment Checklist ✅

## Project Status: READY FOR AWS DEPLOYMENT 🚀

Your BloodBridge application has been fully prepared for AWS deployment with DynamoDB and SNS integration.

---

## What's Been Implemented ✅

### 1. **AWS-Integrated Application** (`app_aws_integrated.py`)
   - ✅ Hybrid mode: Works with both AWS services and local storage (fallback)
   - ✅ DynamoDB integration for users, blood requests, inventory, and emergencies
   - ✅ SNS integration for SMS notifications
   - ✅ Automatic error handling with fallback to local storage
   - ✅ CloudWatch logging ready
   - ✅ Production-grade configuration

### 2. **Updated Dependencies** (`requirements.txt`)
   - ✅ `boto3==1.34.0` - AWS SDK
   - ✅ `botocore==1.34.0` - AWS CLI tools
   - ✅ `awscli==1.44.27` - AWS command-line interface
   - ✅ `gunicorn==21.2.0` - Production WSGI server
   - ✅ `python-dotenv==1.0.0` - Environment variable management

### 3. **Enhanced SNS Helper** (`aws/sns_helper.py`)
   - ✅ Full AWS SNS integration with boto3
   - ✅ SMS notifications to compatible donors
   - ✅ Emergency alert broadcasts
   - ✅ Topic-based notifications
   - ✅ E.164 phone number formatting for international support
   - ✅ Error logging and fallback modes

### 4. **Production Configuration** (`config.py`)
   - ✅ Development, Production, and Testing configurations
   - ✅ AWS credentials management
   - ✅ DynamoDB table configuration
   - ✅ SNS topic configuration
   - ✅ Security best practices (SECRET_KEY enforcement)

### 5. **Environment Configuration** (`.env.example`)
   - ✅ Complete template for AWS deployment settings
   - ✅ Instructions for AWS credentials
   - ✅ Database and SNS configuration
   - ✅ Gunicorn worker settings

### 6. **Production Deployment** (`Procfile`)
   - ✅ Configured for Gunicorn with 4 workers
   - ✅ Proper logging setup
   - ✅ Timeout configuration
   - ✅ Ready for EC2/Heroku deployment

---

## Pre-Deployment Checklist 📋

### Step 1: AWS Account & Credentials
- [ ] Create AWS account (or use existing)
- [ ] Create IAM user with DynamoDB and SNS permissions
- [ ] Generate access key and secret key
- [ ] Install AWS CLI: `pip install awscli`
- [ ] Configure AWS credentials: `aws configure`

### Step 2: Set Up AWS Services

```bash
# 1. Create DynamoDB tables
python aws/dynamodb_setup.py

# 2. Create SNS topics
python aws/sns_setup.py
```

### Step 3: Configure Environment

```bash
# 1. Copy example to actual .env
cp .env.example .env

# 2. Edit .env with your settings:
#    - Change SECRET_KEY to a strong random string
#    - Update AWS_REGION if needed
#    - Update SNS_ALERTS_TOPIC and SNS_EMERGENCY_TOPIC from sns_setup.py output
#    - Set USE_AWS=true for production

# Generate a strong SECRET_KEY:
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 4: Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all requirements
pip install -r requirements.txt
```

### Step 5: Test Locally

```bash
# Set development mode
set FLASK_ENV=development
set USE_AWS=false

# Run application
python app_aws_integrated.py

# Test at http://127.0.0.1:5000
```

### Step 6: Deploy to EC2

```bash
# 1. Launch EC2 instance (Amazon Linux 2 recommended)
#    - Use security group allowing ports 80, 443, 22
#    - Create/use EC2 key pair

# 2. SSH into EC2:
ssh -i your-key.pem ec2-user@your-instance-ip

# 3. On EC2, install Python and dependencies:
sudo yum update -y
sudo yum install python3 python3-pip git -y

# 4. Clone or upload your project:
git clone your-repo.git bloodbridge
cd bloodbridge

# 5. Create virtual environment:
python3 -m venv venv
source venv/bin/activate

# 6. Install dependencies:
pip install -r requirements.txt

# 7. Set environment variables (use IAM role instead of keys):
export FLASK_ENV=production
export USE_AWS=true
export SECRET_KEY='your-generated-secret'
export AWS_REGION='us-east-1'

# 8. Run with Gunicorn:
gunicorn --bind 0.0.0.0:80 --workers 4 --worker-class sync app_aws_integrated:app

# Or use systemd for auto-restart (see below)
```

### Step 7: Set Up Systemd Service (For Auto-Restart)

Create `/etc/systemd/system/bloodbridge.service`:

```ini
[Unit]
Description=BloodBridge Blood Bank Application
After=network.target

[Service]
Type=notify
User=ec2-user
WorkingDirectory=/home/ec2-user/bloodbridge
ExecStart=/home/ec2-user/bloodbridge/venv/bin/gunicorn \
    --bind 0.0.0.0:80 \
    --workers 4 \
    --worker-class sync \
    --timeout 30 \
    --access-logfile /var/log/bloodbridge/access.log \
    --error-logfile /var/log/bloodbridge/error.log \
    app_aws_integrated:app
Restart=always
RestartSec=10
EnvironmentFile=/etc/bloodbridge/.env

[Install]
WantedBy=multi-user.target
```

Then enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable bloodbridge
sudo systemctl start bloodbridge
sudo systemctl status bloodbridge
```

### Step 8: Set Up HTTPS with Let's Encrypt (Recommended)

```bash
# Install certbot
sudo yum install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Update Gunicorn command to use HTTPS...
```

---

## Monitoring & Logging 🔍

### CloudWatch Logs
- Application logs are automatically sent to CloudWatch
- Access via AWS Console → CloudWatch → Log Groups → `/aws/bloodbridge/app`

### Application Health
```bash
# Check application status
sudo systemctl status bloodbridge

# View logs
sudo tail -f /var/log/bloodbridge/error.log
sudo tail -f /var/log/bloodbridge/access.log

# Check EC2 CPU/Memory
# AWS Console → EC2 → Monitoring tab
```

---

## Cost Optimization Tips 💰

1. **DynamoDB**: Use on-demand pricing for variable load
2. **EC2**: Use t2.micro (free tier eligible) for testing
3. **SNS**: Pay per SMS sent (~$0.00645 per SMS in US)
4. **CloudWatch**: Monitor usage to avoid unexpected costs
5. **Set up billing alerts** in AWS Console

---

## Troubleshooting 🔧

### Cannot connect to DynamoDB
- Check IAM user permissions
- Verify AWS_REGION environment variable
- Check DynamoDB table names in `.env`

### SMS not sending
- Verify SNS topic ARNs in `.env`
- Check phone numbers are in E.164 format
- Verify SNS account is in sandbox (needs phone number verification)

### Application crashing
- Check `/var/log/bloodbridge/error.log`
- Verify all environment variables are set
- Ensure DynamoDB tables exist and have correct schema

### High latency
- Check DynamoDB capacity settings
- Monitor CloudWatch metrics
- Consider using DynamoDB caching with ElastiCache

---

## Security Best Practices 🔒

1. ✅ **Change SECRET_KEY** - Generate strong random key
2. ✅ **Use IAM Roles** - Don't put credentials in EC2
3. ✅ **Enable HTTPS** - Use Let's Encrypt or AWS Certificate Manager
4. ✅ **Security Groups** - Restrict access to necessary ports
5. ✅ **DynamoDB Encryption** - Enable encryption at rest
6. ✅ **CloudWatch Monitoring** - Monitor suspicious activity
7. ✅ **Regular Backups** - Use DynamoDB point-in-time recovery

---

## Production Deployment Files

- **`app_aws_integrated.py`** - Main Flask application with AWS integration
- **`config.py`** - Configuration management (dev/prod)
- **`requirements.txt`** - Python dependencies
- **`Procfile`** - Deployment configuration
- **`.env.example`** - Environment variable template
- **`aws/dynamodb_helper.py`** - DynamoDB operations
- **`aws/sns_helper.py`** - SNS notifications
- **`aws/dynamodb_setup.py`** - DynamoDB table creation
- **`aws/sns_setup.py`** - SNS topic creation

---

## Important Notes ⚠️

### About the Dual-Mode Architecture
Your application now supports **two modes**:

1. **Local Development Mode** (`USE_AWS=false`)
   - Uses in-memory storage (lists/dicts)
   - No AWS credentials needed
   - Perfect for testing

2. **AWS Production Mode** (`USE_AWS=true`)
   - Uses DynamoDB for persistence
   - Uses SNS for notifications
   - Requires AWS credentials and services

The application automatically **falls back to local storage** if AWS services are unavailable, ensuring reliability.

### Migration from Local to AWS
You don't need to migrate data! The application:
- Creates new DynamoDB entries when users register
- Continues using in-memory data from previous local deployments
- Automatically uses whichever storage backend is available

---

## Next Steps 🚀

1. ✅ Read this checklist carefully
2. ✅ Follow the "Pre-Deployment Checklist" section
3. ✅ Test locally first with `USE_AWS=false`
4. ✅ Set up AWS services (DynamoDB, SNS)
5. ✅ Launch EC2 instance
6. ✅ Deploy with `USE_AWS=true`
7. ✅ Monitor with CloudWatch
8. ✅ Celebrate! 🎉

---

## Support Resources

- AWS DynamoDB: https://docs.aws.amazon.com/dynamodb/
- AWS SNS: https://docs.aws.amazon.com/sns/
- AWS EC2: https://docs.aws.amazon.com/ec2/
- Gunicorn Docs: https://docs.gunicorn.org/
- Flask Docs: https://flask.palletsprojects.com/

---

**Your BloodBridge application is now AWS-ready! Good luck with your deployment! 🩸❤️**
