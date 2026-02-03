#!/bin/bash
# BloodBridge - AWS Deployment Quick Start Script
# This script automates the initial AWS setup

set -e

echo "╔════════════════════════════════════════════╗"
echo "║  BloodBridge AWS Deployment Setup Script  ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Installing..."
    pip install awscli
fi

echo "✅ AWS CLI found"
echo ""

# Check AWS credentials
echo "Checking AWS credentials..."
if aws sts get-caller-identity &> /dev/null; then
    echo "✅ AWS credentials configured"
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    REGION=$(aws configure get region)
    echo "   Account: $ACCOUNT_ID"
    echo "   Region: $REGION"
else
    echo "❌ AWS credentials not configured"
    echo "Run: aws configure"
    exit 1
fi
echo ""

# Create .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    
    # Generate SECRET_KEY
    SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
    
    # Update .env with values
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/" .env
        sed -i '' "s/us-east-1/$REGION/" .env
    else
        # Linux
        sed -i "s/your-super-secret-key-change-this-in-production/$SECRET_KEY/" .env
        sed -i "s/us-east-1/$REGION/" .env
    fi
    
    echo "✅ .env file created"
    echo "   SECRET_KEY generated: ${SECRET_KEY:0:16}..."
else
    echo "⚠️  .env file already exists, skipping creation"
fi
echo ""

# Set up Python virtual environment
if [ ! -d venv ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create DynamoDB tables
echo "🗄️  Setting up DynamoDB tables..."
python aws/dynamodb_setup.py
echo ""

# Create SNS topics
echo "📢 Setting up SNS topics..."
ALERTS_TOPIC=$(python aws/sns_setup.py | grep "bloodbridge-alerts" | awk '{print $2}')
EMERGENCY_TOPIC=$(python aws/sns_setup.py | grep "bloodbridge-emergency" | awk '{print $2}')

echo "✅ SNS topics created"
echo "   Alerts Topic: $ALERTS_TOPIC"
echo "   Emergency Topic: $EMERGENCY_TOPIC"
echo ""

# Update .env with SNS topics
if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s|arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:bloodbridge-alerts|$ALERTS_TOPIC|" .env
    sed -i '' "s|arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:bloodbridge-emergency|$EMERGENCY_TOPIC|" .env
else
    sed -i "s|arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:bloodbridge-alerts|$ALERTS_TOPIC|" .env
    sed -i "s|arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:bloodbridge-emergency|$EMERGENCY_TOPIC|" .env
fi

echo "✅ .env file updated with SNS topics"
echo ""

echo "╔════════════════════════════════════════════╗"
echo "║  ✅ AWS Setup Complete!                   ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Test locally: python app_aws_integrated.py"
echo "2. When ready to deploy, push to Git"
echo "3. Launch EC2 instance with setup script"
echo ""
echo "For detailed instructions, see AWS_DEPLOYMENT_CHECKLIST.md"
