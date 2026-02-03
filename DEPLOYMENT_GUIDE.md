# BloodBridge - Complete Deployment Guide
## From Local Development to AWS Cloud

---

# Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Local Deployment](#2-local-deployment)
3. [Project File Structure](#3-project-file-structure)
4. [Testing Locally](#4-testing-locally)
5. [AWS Account Setup](#5-aws-account-setup)
6. [EC2 Deployment](#6-ec2-deployment)
7. [DynamoDB Setup](#7-dynamodb-setup)
8. [SNS Setup](#8-sns-setup)
9. [Final Production Deployment](#9-final-production-deployment)
10. [Troubleshooting](#10-troubleshooting)

---

# 1. Prerequisites

## 1.1 Software Requirements

| Software | Version | Download |
|----------|---------|----------|
| Python | 3.8+ | https://python.org |
| pip | Latest | Comes with Python |
| Git | Latest | https://git-scm.com |
| VS Code | Latest | https://code.visualstudio.com |

## 1.2 Check Installation

```bash
# Check Python
python --version
# Output: Python 3.8.x or higher

# Check pip
pip --version
# Output: pip 21.x or higher

# Check Git
git --version
# Output: git version 2.x
```

## 1.3 AWS Requirements (For Cloud Deployment)

- AWS Account (or Troven Labs access)
- AWS CLI installed
- Basic knowledge of EC2, DynamoDB, SNS

---

# 2. Local Deployment

## Step 1: Create Project Directory

```bash
# Windows
mkdir C:\Projects\bloodbridge
cd C:\Projects\bloodbridge

# Mac/Linux
mkdir -p ~/Projects/bloodbridge
cd ~/Projects/bloodbridge
```

## Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

## Step 3: Install Dependencies

```bash
pip install flask werkzeug
```

## Step 4: Create Project Files

Create the following folder structure:

```
bloodbridge/
├── app.py
├── config.py
├── requirements.txt
├── run.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── create_request.html
│   ├── all_requests.html
│   ├── profile.html
│   ├── realtime_dashboard.html
│   ├── blood_inventory.html
│   ├── blood_camps.html
│   ├── sos_emergency.html
│   ├── emergency_list.html
│   ├── leaderboard.html
│   └── error.html
└── aws/
    ├── dynamodb_setup.py
    ├── dynamodb_helper.py
    ├── sns_setup.py
    ├── sns_helper.py
    └── iam_policy.json
```

## Step 5: Run the Application

```bash
python app.py
```

Expected output:
```
============================================================
  BloodBridge - Blood Bank Management System
  URL: http://127.0.0.1:5000
  Demo: john@demo.com / demo123
============================================================

 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

## Step 6: Access the Application

Open browser and go to:
```
http://127.0.0.1:5000
```

## Step 7: Login with Demo Account

| Field | Value |
|-------|-------|
| Email | john@demo.com |
| Password | demo123 |
| Phone | +91-98765-43210 |

---

# 3. Project File Structure

```
bloodbridge/
│
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── run.py                 # Production run script
├── README.md              # Project documentation
├── DEPLOYMENT_GUIDE.md    # This file
│
├── templates/             # HTML Templates (Jinja2)
│   ├── base.html          # Base template with navigation
│   ├── index.html         # Landing page
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── dashboard.html     # User dashboard
│   ├── create_request.html # Create blood request
│   ├── all_requests.html  # View all requests
│   ├── profile.html       # User profile
│   ├── realtime_dashboard.html # Real-time monitoring
│   ├── blood_inventory.html # Blood inventory
│   ├── blood_camps.html   # Donation camps
│   ├── sos_emergency.html # SOS emergency
│   ├── emergency_list.html # Emergency alerts
│   ├── leaderboard.html   # Donor rankings
│   └── error.html         # Error pages
│
└── aws/                   # AWS Integration
    ├── dynamodb_setup.py  # Create DynamoDB tables
    ├── dynamodb_helper.py # DynamoDB CRUD operations
    ├── sns_setup.py       # Create SNS topics
    ├── sns_helper.py      # SNS notifications
    └── iam_policy.json    # IAM permissions
```

---

# 4. Testing Locally

## 4.1 Test Flow

### Test 1: User Registration
1. Go to http://127.0.0.1:5000/register
2. Fill in:
   - Full Name: Test User
   - Email: test@test.com
   - Phone: 9876543210
   - Blood Group: A+
   - Password: test123
3. Click "Create Account"
4. Should redirect to login page

### Test 2: User Login
1. Go to http://127.0.0.1:5000/login
2. Enter: test@test.com / test123
3. Should redirect to dashboard

### Test 3: Create Blood Request
1. Login and go to dashboard
2. Click "New Request"
3. Fill in:
   - Blood Group: A+
   - Location: City Hospital
   - Quantity: 2
   - Urgency: High
4. Click "Submit"
5. Check terminal for SMS notification

### Test 4: Respond to Request
1. Login as different user (john@demo.com)
2. See matching request on dashboard
3. Click "Donate"
4. Request status changes to "Accepted"

### Test 5: Confirm Donation
1. Login as requester
2. Click "Confirm" on accepted request
3. Status changes to "Donated"

### Test 6: SOS Emergency
1. Go to Features → SOS Emergency
2. Fill in emergency details
3. Click "Send SOS"
4. Check terminal for SMS broadcasts

### Test 7: Real-Time Dashboard
1. Go to Features → Real-Time Dashboard
2. See live stats updating every 3 seconds
3. Check blood inventory levels
4. View activity feed

## 4.2 Verify SMS Output

When actions occur, check terminal for SMS logs:

```
==================================================
📱 SMS NOTIFICATION
==================================================
To: +919876543210
Message: 🩸 A+ blood needed at City Hospital...
==================================================
```

---

# 5. AWS Account Setup

## 5.1 Using Troven Labs (Temporary Access)

If using Troven Labs for AWS access:
1. Login to Troven Labs portal
2. Get temporary AWS credentials
3. Note down: Access Key, Secret Key, Region

## 5.2 Configure AWS CLI

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure
```

Enter when prompted:
```
AWS Access Key ID: YOUR_ACCESS_KEY
AWS Secret Access Key: YOUR_SECRET_KEY
Default region name: us-east-1
Default output format: json
```

## 5.3 Verify AWS Access

```bash
aws sts get-caller-identity
```

Should show your AWS account details.

---

# 6. EC2 Deployment

## Step 1: Launch EC2 Instance

1. Go to AWS Console → EC2 → Launch Instance
2. Configure:
   - **Name**: BloodBridge-Server
   - **AMI**: Amazon Linux 2023
   - **Instance Type**: t2.micro (free tier)
   - **Key Pair**: Create new → Download .pem file
   - **Security Group**: Allow SSH (22), HTTP (80), Custom (5000)

## Step 2: Connect to EC2

```bash
# Set permissions on key file
chmod 400 bloodbridge-key.pem

# Connect via SSH
ssh -i bloodbridge-key.pem ec2-user@YOUR_EC2_PUBLIC_IP
```

## Step 3: Install Dependencies on EC2

```bash
# Update system
sudo yum update -y

# Install Python
sudo yum install python3 python3-pip -y

# Install Git
sudo yum install git -y

# Verify installations
python3 --version
pip3 --version
```

## Step 4: Clone/Upload Project

### Option A: Using Git
```bash
# Clone from GitHub (if you have a repo)
git clone https://github.com/yourusername/bloodbridge.git
cd bloodbridge
```

### Option B: Using SCP (Upload files)
```bash
# From your local machine
scp -i bloodbridge-key.pem -r ./bloodbridge ec2-user@YOUR_EC2_IP:~/
```

## Step 5: Install Python Packages

```bash
cd bloodbridge
pip3 install -r requirements.txt
```

## Step 6: Run Application

### Development Mode (Port 5000)
```bash
python3 app.py
```

### Production Mode (Port 80)
```bash
sudo python3 run.py
```

## Step 7: Access Application

Open browser:
```
http://YOUR_EC2_PUBLIC_IP
```

---

# 7. DynamoDB Setup

## Step 1: Install boto3

```bash
pip install boto3
```

## Step 2: Create Tables

```bash
python aws/dynamodb_setup.py
```

Output:
```
==================================================
  BloodBridge - DynamoDB Setup
==================================================

Region: us-east-1

Creating tables...

✅ Table 'bloodbridge_users' created successfully!
✅ Table 'bloodbridge_requests' created successfully!
✅ Table 'bloodbridge_inventory' created successfully!
✅ Blood inventory initialized!

==================================================
  Setup Complete!
==================================================
```

## Step 3: Verify Tables

```bash
aws dynamodb list-tables
```

Output:
```json
{
    "TableNames": [
        "bloodbridge_inventory",
        "bloodbridge_requests",
        "bloodbridge_users"
    ]
}
```

## Step 4: Update app.py for DynamoDB

In `app.py`, find comments like:
```python
# TODO [DynamoDB]: Replace with put_item()
users_db.append(new_user)
```

Replace with:
```python
from aws.dynamodb_helper import create_user
create_user(new_user)
```

---

# 8. SNS Setup

## Step 1: Create SNS Topics

```bash
python aws/sns_setup.py
```

Output:
```
==================================================
  BloodBridge - SNS Setup
==================================================

Region: us-east-1

Creating SNS topics...

✅ Topic 'bloodbridge-alerts' created!
   ARN: arn:aws:sns:us-east-1:123456789:bloodbridge-alerts

✅ Topic 'bloodbridge-emergency' created!
   ARN: arn:aws:sns:us-east-1:123456789:bloodbridge-emergency

📄 Topic ARNs saved to aws/sns_topics.txt

==================================================
  Setup Complete!
==================================================
```

## Step 2: Update sns_helper.py

Update the Topic ARNs in `aws/sns_helper.py`:
```python
ALERTS_TOPIC_ARN = 'arn:aws:sns:us-east-1:YOUR_ACCOUNT:bloodbridge-alerts'
EMERGENCY_TOPIC_ARN = 'arn:aws:sns:us-east-1:YOUR_ACCOUNT:bloodbridge-emergency'
```

## Step 3: Enable Real SMS

In `aws/sns_helper.py`, uncomment the boto3 code:
```python
import boto3
sns = boto3.client('sns', region_name='us-east-1')

def send_sms(phone_number, message):
    response = sns.publish(
        PhoneNumber=format_phone_e164(phone_number),
        Message=message[:160]
    )
    return response['MessageId']
```

---

# 9. Final Production Deployment

## Step 1: Set Environment Variables

```bash
export FLASK_ENV=production
export SECRET_KEY=your-super-secret-key-here
export AWS_REGION=us-east-1
```

## Step 2: Run with Gunicorn

```bash
# Install Gunicorn
pip3 install gunicorn

# Run on port 80
sudo gunicorn --bind 0.0.0.0:80 app:app --workers 4
```

## Step 3: Create Systemd Service

```bash
sudo nano /etc/systemd/system/bloodbridge.service
```

Add:
```ini
[Unit]
Description=BloodBridge Flask Application
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/bloodbridge
Environment="FLASK_ENV=production"
ExecStart=/usr/local/bin/gunicorn --bind 0.0.0.0:80 app:app --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable bloodbridge
sudo systemctl start bloodbridge
```

## Step 4: Verify Deployment

```bash
# Check service status
sudo systemctl status bloodbridge

# Check logs
sudo journalctl -u bloodbridge -f
```

---

# 10. Troubleshooting

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `ModuleNotFoundError: flask` | Flask not installed | `pip install flask` |
| `Address already in use` | Port 5000 in use | Kill process: `kill $(lsof -t -i:5000)` |
| `TemplateNotFound` | Missing template | Check templates folder |
| `Permission denied (port 80)` | Need sudo | Run with `sudo` |
| `Connection refused` | App not running | Start with `python app.py` |
| `502 Bad Gateway` | Gunicorn crashed | Check logs: `journalctl -u bloodbridge` |

## Debug Mode

To see detailed errors:
```python
# In app.py
app.run(debug=True)
```

## Check Logs

```bash
# Application logs
tail -f /var/log/bloodbridge.log

# System logs
sudo journalctl -u bloodbridge -f
```

## Test Database Connection

```python
python -c "from aws.dynamodb_helper import get_user_by_email; print(get_user_by_email('john@demo.com'))"
```

## Test SNS

```python
python -c "from aws.sns_helper import send_sms; send_sms('+919876543210', 'Test message')"
```

---

# Quick Reference

## Local Development
```bash
python app.py
# Open: http://127.0.0.1:5000
```

## EC2 Production
```bash
sudo gunicorn --bind 0.0.0.0:80 app:app -w 4
# Open: http://YOUR_EC2_IP
```

## Demo Login
- Email: john@demo.com
- Password: demo123
- Phone: +91-98765-43210

---

**BloodBridge - Every Drop Counts! 🩸**