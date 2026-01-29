#!/usr/bin/env python3
"""
BloodBridge - AWS Deployment Script
===================================
This script helps deploy BloodBridge to AWS step by step.

Usage:
    python deploy_aws.py --step 1  # Configure AWS
    python deploy_aws.py --step 2  # Set up DynamoDB
    python deploy_aws.py --step 3  # Set up SNS
    python deploy_aws.py --step 4  # Prepare for EC2 deployment
"""

import os
import sys
import subprocess
import argparse

def print_header(step, title):
    """Print step header."""
    print("\n" + "="*60)
    print(f"  STEP {step}: {title}")
    print("="*60 + "\n")

def step_1_configure_aws():
    """Step 1: Configure AWS credentials."""
    print_header(1, "Configure AWS Credentials")
    
    print("Running: aws configure")
    print("Please enter your AWS credentials when prompted:")
    print("- AWS Access Key ID")
    print("- AWS Secret Access Key") 
    print("- Default region: us-east-1")
    print("- Default output format: json\n")
    
    try:
        result = subprocess.run(['aws', 'configure'], check=True)
        if result.returncode == 0:
            print("✅ AWS credentials configured successfully!")
            return True
    except subprocess.CalledProcessError:
        print("❌ Failed to configure AWS credentials")
        return False
    except FileNotFoundError:
        print("❌ AWS CLI not found. Please install it first.")
        return False

def step_2_setup_dynamodb():
    """Step 2: Set up DynamoDB tables."""
    print_header(2, "Set up DynamoDB Tables")
    
    print("Creating DynamoDB tables...")
    print("Tables to be created:")
    print("- bloodbridge_users")
    print("- bloodbridge_requests") 
    print("- bloodbridge_inventory\n")
    
    try:
        result = subprocess.run([sys.executable, 'aws/dynamodb_setup.py'], 
                              cwd=os.getcwd(), check=True)
        if result.returncode == 0:
            print("✅ DynamoDB tables created successfully!")
            return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create DynamoDB tables")
        return False
    except FileNotFoundError:
        print("❌ dynamodb_setup.py not found")
        return False

def step_3_setup_sns():
    """Step 3: Set up SNS topics."""
    print_header(3, "Set up SNS Notification Topics")
    
    print("Creating SNS topics...")
    print("Topics to be created:")
    print("- bloodbridge-alerts")
    print("- bloodbridge-emergency\n")
    
    try:
        result = subprocess.run([sys.executable, 'aws/sns_setup.py'], 
                              cwd=os.getcwd(), check=True)
        if result.returncode == 0:
            print("✅ SNS topics created successfully!")
            return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create SNS topics")
        return False
    except FileNotFoundError:
        print("❌ sns_setup.py not found")
        return False

def step_4_prepare_ec2():
    """Step 4: Prepare for EC2 deployment."""
    print_header(4, "Prepare for EC2 Deployment")
    
    print("✅ Your project is ready for EC2 deployment!")
    print("\nNext steps:")
    print("1. Launch an EC2 instance (Amazon Linux 2)")
    print("2. Upload your project files to the instance")
    print("3. Install dependencies: pip install -r requirements.txt")
    print("4. Run: gunicorn --bind 0.0.0.0:80 app:app")
    print("\nRequired files for deployment:")
    print("- app.py")
    print("- requirements.txt")
    print("- aws/ folder")
    print("- templates/ folder")
    print("- config.py")
    print("- run.py")
    
    return True

def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description='BloodBridge AWS Deployment')
    parser.add_argument('--step', type=int, choices=[1,2,3,4], 
                       help='Deployment step to execute')
    
    args = parser.parse_args()
    
    if not args.step:
        print("BloodBridge - AWS Deployment Assistant")
        print("="*50)
        print("Available steps:")
        print("  --step 1 : Configure AWS credentials")
        print("  --step 2 : Set up DynamoDB tables")
        print("  --step 3 : Set up SNS topics")
        print("  --step 4 : Prepare for EC2 deployment")
        print("\nExample: python deploy_aws.py --step 1")
        return
    
    success = False
    
    if args.step == 1:
        success = step_1_configure_aws()
    elif args.step == 2:
        # Check if AWS is configured first
        try:
            subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                         check=True, capture_output=True)
            success = step_2_setup_dynamodb()
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Please configure AWS credentials first (step 1)")
            success = False
    elif args.step == 3:
        # Check if AWS is configured first
        try:
            subprocess.run(['aws', 'sts', 'get-caller-identity'], 
                         check=True, capture_output=True)
            success = step_3_setup_sns()
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Please configure AWS credentials first (step 1)")
            success = False
    elif args.step == 4:
        success = step_4_prepare_ec2()
    
    if success:
        print(f"\n✅ Step {args.step} completed successfully!")
    else:
        print(f"\n❌ Step {args.step} failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()