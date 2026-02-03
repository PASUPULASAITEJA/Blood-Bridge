"""
BloodBridge - SNS Helper Functions
===================================
This module provides helper functions for SMS and email notifications using AWS SNS.

Usage:
    from aws.sns_helper import send_sms, send_emergency_alert, notify_donors

Phone numbers should be in E.164 format: +919876543210
"""
import os
import boto3
import logging
from botocore.exceptions import ClientError
import re

# Configuration
logger = logging.getLogger(__name__)
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
SNS_ENABLED = os.getenv('SNS_ENABLED', 'true').lower() == 'true'

# Initialize SNS client
try:
    sns = boto3.client('sns', region_name=AWS_REGION)
    logger.info("✅ SNS client initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize SNS client: {e}")
    SNS_ENABLED = False

# Topic ARNs (Update these after running sns_setup.py)
ALERTS_TOPIC_ARN = os.getenv('SNS_ALERTS_TOPIC', 'arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:bloodbridge-alerts')
EMERGENCY_TOPIC_ARN = os.getenv('SNS_EMERGENCY_TOPIC', 'arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:bloodbridge-emergency')


def format_phone_e164(phone):
    """
    Format phone number to E.164 format for AWS SNS.
    E.164 format: +[country code][number]
    Example: +919876543210
    """
    # Remove all non-digits except leading +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # If doesn't start with +, assume Indian number
    if not cleaned.startswith('+'):
        if cleaned.startswith('91') and len(cleaned) == 12:
            cleaned = '+' + cleaned
        elif len(cleaned) == 10:
            cleaned = '+91' + cleaned
        else:
            # Default to +1 for other countries
            cleaned = '+1' + cleaned.lstrip('+')
    
    return cleaned


def send_sms(phone_number, message):
    """
    Send SMS to a single phone number using AWS SNS.
    
    Args:
        phone_number (str): Phone number (any format, will be converted to E.164)
        message (str): SMS message (max 160 chars for single SMS)
    
    Returns:
        str: Message ID if successful, None otherwise
    
    Raises:
        ClientError: If SNS publish fails
    """
    if not SNS_ENABLED:
        logger.warning(f"[DEV MODE] SMS not sent (SNS disabled): {phone_number[:10]}...")
        return "DEV_MODE_MSG_ID"
    
    try:
        formatted_phone = format_phone_e164(phone_number)
        
        response = sns.publish(
            PhoneNumber=formatted_phone,
            Message=message[:160],
            MessageAttributes={
                'AWS.SNS.SMS.SenderID': {
                    'DataType': 'String',
                    'StringValue': 'BloodBridge'
                },
                'AWS.SNS.SMS.SMSType': {
                    'DataType': 'String',
                    'StringValue': 'Transactional'
                }
            }
        )
        logger.info(f"✅ SMS sent to {formatted_phone}: {response['MessageId']}")
        return response['MessageId']
    
    except ClientError as e:
        logger.error(f"❌ Failed to send SMS to {phone_number}: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error sending SMS: {e}")
        raise


def send_emergency_alert(blood_group, location, urgency, requester_name):
    """
    Broadcast emergency alert to all subscribers.
    
    Args:
        blood_group (str): Blood type needed
        location (str): Emergency location
        urgency (str): Urgency level
        requester_name (str): Who needs blood
    
    Returns:
        str: Message ID if successful
    """
    if not SNS_ENABLED:
        logger.warning(f"[DEV MODE] Emergency alert not broadcast (SNS disabled)")
        return "DEV_MODE_EMERGENCY_ID"
    
    try:
        subject = f"🆘 EMERGENCY: {blood_group} Blood Needed"
        message = f"EMERGENCY ALERT!\n\nBlood Type: {blood_group}\nLocation: {location}\nUrgency: {urgency.upper()}\nRequester: {requester_name}\n\nOpen BloodBridge now to help save a life!"
        
        response = sns.publish(
            TopicArn=EMERGENCY_TOPIC_ARN,
            Subject=subject,
            Message=message,
            MessageAttributes={
                'urgency': {
                    'DataType': 'String',
                    'StringValue': urgency
                }
            }
        )
        logger.info(f"✅ Emergency alert broadcast: {response['MessageId']}")
        return response['MessageId']
    
    except ClientError as e:
        logger.error(f"❌ Failed to broadcast emergency: {e}")
        raise


def send_alert(subject, message, topic_arn=None):
    """
    Send alert notification to a topic.
    
    Args:
        subject (str): Alert subject
        message (str): Alert message
        topic_arn (str): SNS Topic ARN (defaults to ALERTS_TOPIC_ARN)
    
    Returns:
        str: Message ID if successful
    """
    if not SNS_ENABLED:
        logger.warning(f"[DEV MODE] Alert not sent (SNS disabled)")
        return "DEV_MODE_ALERT_ID"
    
    try:
        response = sns.publish(
            TopicArn=topic_arn or ALERTS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
        logger.info(f"✅ Alert sent: {response['MessageId']}")
        return response['MessageId']
    
    except ClientError as e:
        logger.error(f"❌ Failed to send alert: {e}")
        raise


# ============================================
# SPECIALIZED NOTIFICATION FUNCTIONS
# ============================================

def send_welcome_sms(phone_number, user_name):
    """Send welcome SMS to new user."""
    message = f"Welcome to BloodBridge, {user_name}! 🩸 You're now part of a lifesaving community. Every drop counts!"
    return send_sms(phone_number, message)


def send_blood_request_sms(phone_number, blood_group, location, urgency, requester_phone):
    """Notify a compatible donor about a new blood request."""
    urgency_text = "URGENT! " if urgency in ['critical', 'high'] else ""
    message = f"🩸 {urgency_text}{blood_group} blood needed at {location}. Contact: {requester_phone}. Open BloodBridge to respond."
    return send_sms(phone_number, message)


def send_donor_found_sms(requester_phone, donor_name, donor_phone, blood_group):
    """Notify requester that a donor has been found."""
    message = f"🎉 DONOR FOUND! {donor_name} ({blood_group}) will donate. Contact: {donor_phone}. BloodBridge"
    return send_sms(requester_phone, message)


def send_donation_confirmed_sms(donor_phone, donor_name):
    """Send thank you SMS to donor after confirmed donation."""
    message = f"❤️ Thank you {donor_name}! Your donation confirmed. You've helped save up to 3 lives! - BloodBridge"
    return send_sms(donor_phone, message)


def send_camp_reminder_sms(phone_number, camp_name, camp_date, camp_location):
    """Send blood camp reminder SMS."""
    message = f"🏕️ Reminder: {camp_name} on {camp_date} at {camp_location}. See you there! - BloodBridge"
    return send_sms(phone_number, message)


def notify_donors_batch(phones, blood_group, location, urgency, requester_phone):
    """
    Send SMS notifications to multiple donors.
    
    Args:
        phones (list): List of phone numbers
        blood_group (str): Blood type needed
        location (str): Location
        urgency (str): Urgency level
        requester_phone (str): Contact phone
    
    Returns:
        tuple: (success_count, failed_count)
    """
    success_count = 0
    failed_count = 0
    
    for phone in phones:
        try:
            send_blood_request_sms(phone, blood_group, location, urgency, requester_phone)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to notify {phone}: {e}")
            failed_count += 1
    
    logger.info(f"Batch notification: {success_count} sent, {failed_count} failed")
    return success_count, failed_count


def subscribe_to_emergency_alerts(phone_number):
    """
    Subscribe a phone number to emergency alerts via SMS.
    
    Args:
        phone_number (str): Phone number to subscribe
    
    Returns:
        str: Subscription ARN if successful
    """
    if not SNS_ENABLED:
        logger.warning(f"[DEV MODE] Not subscribed to topic (SNS disabled)")
        return "DEV_MODE_SUBSCRIPTION_ARN"
    
    try:
        formatted_phone = format_phone_e164(phone_number)
        response = sns.subscribe(
            TopicArn=EMERGENCY_TOPIC_ARN,
            Protocol='sms',
            Endpoint=formatted_phone
        )
        logger.info(f"✅ Subscribed {formatted_phone} to emergency alerts")
        return response['SubscriptionArn']
    
    except ClientError as e:
        logger.error(f"❌ Failed to subscribe: {e}")
        raise


def get_topic_attributes(topic_arn):
    """Get topic attributes like subscription count."""
    try:
        response = sns.get_topic_attributes(TopicArn=topic_arn)
        return response['Attributes']
    except ClientError as e:
        logger.error(f"❌ Failed to get topic attributes: {e}")
        raise
