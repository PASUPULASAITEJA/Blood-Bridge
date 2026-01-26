"""
BloodBridge - SNS Setup Script
==============================
This script creates SNS topics for BloodBridge notifications.

Prerequisites:
1. AWS CLI configured with credentials
2. boto3 installed (pip install boto3)

Usage:
    python aws/sns_setup.py

Topics Created:
1. bloodbridge-alerts - General blood request alerts
2. bloodbridge-emergency - Critical emergency alerts
"""

import boto3
from botocore.exceptions import ClientError

# Configuration
AWS_REGION = 'us-east-1'  # Change as needed


def create_sns_topics(sns_client):
    """
    Create SNS topics for notifications.
    """
    topics = {}
    
    # Topic 1: General Alerts
    try:
        response = sns_client.create_topic(
            Name='bloodbridge-alerts',
            Tags=[
                {'Key': 'Project', 'Value': 'BloodBridge'},
                {'Key': 'Type', 'Value': 'Alerts'}
            ]
        )
        topics['alerts'] = response['TopicArn']
        print(f"✅ Topic 'bloodbridge-alerts' created!")
        print(f"   ARN: {response['TopicArn']}")
    except ClientError as e:
        print(f"❌ Error creating alerts topic: {e}")
    
    # Topic 2: Emergency Alerts
    try:
        response = sns_client.create_topic(
            Name='bloodbridge-emergency',
            Tags=[
                {'Key': 'Project', 'Value': 'BloodBridge'},
                {'Key': 'Type', 'Value': 'Emergency'}
            ]
        )
        topics['emergency'] = response['TopicArn']
        print(f"✅ Topic 'bloodbridge-emergency' created!")
        print(f"   ARN: {response['TopicArn']}")
    except ClientError as e:
        print(f"❌ Error creating emergency topic: {e}")
    
    return topics


def subscribe_email(sns_client, topic_arn, email):
    """
    Subscribe an email address to a topic.
    The subscriber will receive a confirmation email.
    """
    try:
        response = sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=email
        )
        print(f"✅ Subscription pending for {email}")
        print(f"   Check inbox to confirm subscription.")
        return response['SubscriptionArn']
    except ClientError as e:
        print(f"❌ Error subscribing email: {e}")
        return None


def subscribe_sms(sns_client, topic_arn, phone_number):
    """
    Subscribe a phone number to a topic for SMS.
    Phone number should be in E.164 format (+1234567890)
    """
    try:
        response = sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol='sms',
            Endpoint=phone_number
        )
        print(f"✅ SMS subscription created for {phone_number}")
        return response['SubscriptionArn']
    except ClientError as e:
        print(f"❌ Error subscribing phone: {e}")
        return None


def publish_message(sns_client, topic_arn, subject, message):
    """
    Publish a message to a topic.
    All subscribers will receive the message.
    """
    try:
        response = sns_client.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=message
        )
        print(f"✅ Message published! MessageId: {response['MessageId']}")
        return response['MessageId']
    except ClientError as e:
        print(f"❌ Error publishing message: {e}")
        return None


def publish_sms(sns_client, phone_number, message):
    """
    Send SMS directly to a phone number (without topic).
    """
    try:
        response = sns_client.publish(
            PhoneNumber=phone_number,
            Message=message
        )
        print(f"✅ SMS sent! MessageId: {response['MessageId']}")
        return response['MessageId']
    except ClientError as e:
        print(f"❌ Error sending SMS: {e}")
        return None


def main():
    """Main function to set up SNS."""
    print("\n" + "="*50)
    print("  BloodBridge - SNS Setup")
    print("="*50 + "\n")
    
    # Initialize SNS client
    sns = boto3.client('sns', region_name=AWS_REGION)
    
    print(f"Region: {AWS_REGION}\n")
    print("Creating SNS topics...\n")
    
    # Create topics
    topics = create_sns_topics(sns)
    
    # Save topic ARNs to a file for reference
    if topics:
        with open('aws/sns_topics.txt', 'w') as f:
            for name, arn in topics.items():
                f.write(f"{name}={arn}\n")
        print("\n📄 Topic ARNs saved to aws/sns_topics.txt")
    
    print("\n" + "="*50)
    print("  Setup Complete!")
    print("="*50)
    print("\nNext Steps:")
    print("1. Update app.py with the Topic ARNs")
    print("2. Subscribe emails/phones to topics")
    print("3. Test by publishing a message")
    print("\nExample usage in app.py:")
    print("  from aws.sns_helper import send_notification")
    print("  send_notification('Blood Request', 'O+ needed at City Hospital')")
    print()


if __name__ == '__main__':
    main()
