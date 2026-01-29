# BloodBridge - AWS Deployment Preparation Guide

## 🚀 **Ready for AWS Deployment**

Your BloodBridge project is now prepared for AWS deployment with all necessary dependencies installed and configured.

## ✅ **What's Been Done**

1. **AWS Dependencies Installed**:
   - `boto3==1.42.37` (compatible with AWS CLI)
   - `awscli==1.44.27`
   - `gunicorn==21.2.0` (for production serving)

2. **Requirements Updated**:
   - Enabled AWS SDK and production server in `requirements.txt`

3. **Virtual Environment Ready**:
   - Clean `venv/` folder with all dependencies
   - No conflicts between packages

## 📋 **Next Steps for AWS Deployment**

### 1. **Configure AWS Credentials**
```powershell
# Run this command and enter your AWS credentials:
aws configure

# You'll need to provide:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region: us-east-1
# - Default output format: json
```

### 2. **Set Up AWS Services**
```powershell
# Create DynamoDB tables
python aws/dynamodb_setup.py

# Create SNS notification topics
python aws/sns_setup.py
```

### 3. **Update Application for AWS**
Modify `app.py` to use AWS services instead of in-memory storage:

```python
# In app.py, replace in-memory storage with DynamoDB calls
# Example changes needed:
# users_db.append(new_user) → create_user(new_user)
# get_user_by_email(email) → dynamodb_get_user_by_email(email)
```

### 4. **Deploy to EC2**
1. Launch an EC2 instance (Amazon Linux 2 recommended)
2. Upload your project files
3. Install dependencies: `pip install -r requirements.txt`
4. Run with Gunicorn: `gunicorn --bind 0.0.0.0:80 app:app`

## 🛠️ **AWS Services Used**

- **DynamoDB**: User data, blood requests, inventory
- **SNS**: SMS notifications and alerts
- **EC2**: Application hosting
- **IAM**: Access control and security

## 🔧 **Environment Variables Needed**

Set these in your production environment:
```bash
export FLASK_ENV=production
export SECRET_KEY=your-super-secret-key
export AWS_REGION=us-east-1
```

## 📦 **Deployment Ready Files**

- ✅ `requirements.txt` - All dependencies including AWS
- ✅ `aws/` folder - DynamoDB and SNS setup scripts
- ✅ `run.py` - Production runner with Gunicorn
- ✅ `venv/` - Virtual environment with all packages

## ⚠️ **Before Going Live**

1. Change the secret key in `app.py`
2. Set up proper SSL certificate
3. Configure security groups for EC2
4. Set up monitoring and logging
5. Test all features thoroughly

Your BloodBridge project is now fully prepared for AWS deployment!