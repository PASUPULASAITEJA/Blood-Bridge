"""
BloodBridge - SNS Helper Functions
===================================
This module provides helper functions for SMS and email notifications.
Currently prints to console. When deploying to AWS, uncomment boto3 code.

Usage:
    from aws.sns_helper import send_sms, send_emergency_sms, notify_donors

Phone numbers should be in E.164 format: +919876543210
"""

# TODO [SNS]: Uncomment these lines when deploying to AWS
# import boto3
# from botocore.exceptions import ClientError

# Configuration
AWS_REGION = 'us-east-1'

# Topic ARNs (Update these after running sns_setup.py)
ALERTS_TOPIC_ARN = 'arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:bloodbridge-alerts'
EMERGENCY_TOPIC_ARN = 'arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:bloodbridge-emergency'

# TODO [SNS]: Uncomment when deploying to AWS
# sns = boto3.client('sns', region_name=AWS_REGION)


def format_phone_e164(phone):
    """
    Format phone number to E.164 format for AWS SNS.
    E.164 format: +[country code][number]
    Example: +919876543210
    """
    import re
    # Remove all non-digits except leading +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # If doesn't start with +, assume Indian number
    if not cleaned.startswith('+'):
        if cleaned.startswith('91') and len(cleaned) == 12:
            cleaned = '+' + cleaned
        elif len(cleaned) == 10:
            cleaned = '+91' + cleaned
        else:
            cleaned = '+' + cleaned
    
    return cleaned


def send_sms(phone_number, message):
    """
    Send SMS to a single phone number.
    
    Args:
        phone_number (str): Phone number (any format, will be converted to E.164)
        message (str): SMS message (max 160 chars for single SMS)
    
    Returns:
        str or None: Message ID if successful
    
    TODO [SNS]: Replace print with actual SNS call:
        response = sns.publish(
            PhoneNumber=format_phone_e164(phone_number),
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
        return response['MessageId']
    """
    formatted_phone = format_phone_e164(phone_number)
    print(f"\n{'='*50}")
    print(f"📱 SMS NOTIFICATION")
    print(f"{'='*50}")
    print(f"To: {formatted_phone}")
    print(f"Message: {message[:160]}")
    print(f"{'='*50}\n")
    return "LOCAL_MSG_ID"


def send_emergency_sms(phone_number, blood_group, location, requester_name, contact_phone):
    """
    Send emergency SOS SMS.
    
    Args:
        phone_number (str): Recipient phone
        blood_group (str): Blood type needed
        location (str): Emergency location
        requester_name (str): Who needs blood
        contact_phone (str): Contact number for the emergency
    
    Returns:
        str or None: Message ID
    """
    message = f"🆘 EMERGENCY: {blood_group} blood needed URGENTLY at {location}! Contact {requester_name}: {contact_phone}. Please help if you can!"
    return send_sms(phone_number, message)


def send_donor_found_sms(requester_phone, donor_name, donor_phone, blood_group):
    """
    Notify requester that a donor has been found.
    
    Args:
        requester_phone (str): Requester's phone
        donor_name (str): Donor's name
        donor_phone (str): Donor's phone
        blood_group (str): Blood type
    
    Returns:
        str or None: Message ID
    """
    message = f"🎉 DONOR FOUND! {donor_name} ({blood_group}) will donate. Contact: {donor_phone}. BloodBridge"
    return send_sms(requester_phone, message)


def send_donation_confirmed_sms(donor_phone, donor_name):
    """
    Send thank you SMS to donor after confirmed donation.
    
    Args:
        donor_phone (str): Donor's phone
        donor_name (str): Donor's name
    
    Returns:
        str or None: Message ID
    """
    message = f"❤️ Thank you {donor_name}! Your blood donation is confirmed. You've helped save up to 3 lives! - BloodBridge"
    return send_sms(donor_phone, message)


def send_blood_request_sms(phone_number, blood_group, location, urgency, requester_phone):
    """
    Notify a compatible donor about a new blood request.
    
    Args:
        phone_number (str): Donor's phone
        blood_group (str): Blood type needed
        location (str): Request location
        urgency (str): Urgency level
        requester_phone (str): Requester's contact
    
    Returns:
        str or None: Message ID
    """
    urgency_text = "URGENT! " if urgency in ['critical', 'high'] else ""
    message = f"🩸 {urgency_text}{blood_group} blood needed at {location}. Contact: {requester_phone}. Open BloodBridge to respond."
    return send_sms(phone_number, message)


def send_camp_reminder_sms(phone_number, camp_name, camp_date, camp_location):
    """
    Send blood camp reminder SMS.
    
    Args:
        phone_number (str): Donor's phone
        camp_name (str): Camp name
        camp_date (str): Camp date
        camp_location (str): Camp location
    
    Returns:
        str or None: Message ID
    """
    message = f"🏕️ Reminder: {camp_name} on {camp_date} at {camp_location}. See you there! - BloodBridge"
    return send_sms(phone_number, message)


def send_welcome_sms(phone_number, user_name):
    """
    Send welcome SMS to new user.
    
    Args:
        phone_number (str): User's phone
        user_name (str): User's name
    
    Returns:
        str or None: Message ID
    """
    message = f"Welcome to BloodBridge, {user_name}! 🩸 You're now part of a lifesaving community. Every drop counts!"
    return send_sms(phone_number, message)


def notify_compatible_donors(donors_list, blood_group, location, urgency, requester_phone):
    """
    Notify all compatible donors about a blood request.
    
    Args:
        donors_list (list): List of donor dicts with 'phone' key
        blood_group (str): Blood type needed
        location (str): Request location
        urgency (str): Urgency level
        requester_phone (str): Requester's contact
    
    Returns:
        int: Number of SMS sent
    """
    count = 0
    for donor in donors_list:
        phone = donor.get('phone')
        if phone:
            send_blood_request_sms(phone, blood_group, location, urgency, requester_phone)
            count += 1
    
    print(f"[SMS] Notified {count} compatible donors")
    return count


def broadcast_emergency(donors_list, blood_group, location, hospital, contact_phone, requester_name):
    """
    Broadcast emergency to all compatible donors.
    
    Args:
        donors_list (list): List of donor dicts
        blood_group (str): Blood type needed
        location (str): Emergency location
        hospital (str): Hospital name
        contact_phone (str): Emergency contact
        requester_name (str): Requester's name
    
    Returns:
        int: Number of SMS sent
    """
    count = 0
    for donor in donors_list:
        phone = donor.get('phone')
        if phone:
            message = f"🆘 EMERGENCY at {hospital}! {blood_group} blood needed NOW! Location: {location}. Call: {contact_phone}. Help save a life!"
            send_sms(phone, message)
            count += 1
    
    print(f"[EMERGENCY] Broadcast sent to {count} donors")
    return count


# ============================================
# EMAIL NOTIFICATIONS (Topic-based)
# ============================================

def send_topic_notification(subject, message, topic_arn=None):
    """
    Send notification to all subscribers of a topic.
    Used for email notifications.
    
    Args:
        subject (str): Email subject
        message (str): Email body
        topic_arn (str): SNS Topic ARN
    
    Returns:
        str or None: Message ID
    
    TODO [SNS]: Replace with:
        response = sns.publish(
            TopicArn=topic_arn or ALERTS_TOPIC_ARN,
            Subject=subject,
            Message=message
        )
        return response['MessageId']
    """
    print(f"\n{'='*50}")
    print(f"📧 TOPIC NOTIFICATION")
    print(f"{'='*50}")
    print(f"Topic: {topic_arn or ALERTS_TOPIC_ARN}")
    print(f"Subject: {subject}")
    print(f"Message: {message[:200]}...")
    print(f"{'='*50}\n")
    return "LOCAL_TOPIC_MSG_ID"


def subscribe_phone_to_topic(phone_number, topic_arn=None):
    """
    Subscribe a phone number to receive topic notifications via SMS.
    
    Args:
        phone_number (str): Phone number to subscribe
        topic_arn (str): Topic ARN
    
    Returns:
        str or None: Subscription ARN
    
    TODO [SNS]: Replace with:
        response = sns.subscribe(
            TopicArn=topic_arn or EMERGENCY_TOPIC_ARN,
            Protocol='sms',
            Endpoint=format_phone_e164(phone_number)
        )
        return response['SubscriptionArn']
    """
    formatted = format_phone_e164(phone_number)
    print(f"[SNS] Subscribed {formatted} to topic")
    return "LOCAL_SUBSCRIPTION_ARN"


def subscribe_email_to_topic(email, topic_arn=None):
    """
    Subscribe an email to receive topic notifications.
    User will receive confirmation email.
    
    Args:
        email (str): Email address
        topic_arn (str): Topic ARN
    
    Returns:
        str or None: Subscription ARN
    
    TODO [SNS]: Replace with:
        response = sns.subscribe(
            TopicArn=topic_arn or ALERTS_TOPIC_ARN,
            Protocol='email',
            Endpoint=email
        )
        return response['SubscriptionArn']
    """
    print(f"[SNS] Subscription pending for {email}")
    return "LOCAL_EMAIL_SUBSCRIPTION_ARN"
