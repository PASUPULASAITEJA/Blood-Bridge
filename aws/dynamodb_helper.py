"""
BloodBridge - DynamoDB Helper Functions
=======================================
This module provides helper functions for DynamoDB operations.
Replace local storage calls with these functions when deploying to AWS.

Usage:
    from aws.dynamodb_helper import (
        create_user, get_user_by_email, get_user_by_id, get_user_by_phone,
        create_blood_request, get_blood_request, update_blood_request,
        get_user_blood_requests, get_all_pending_requests,
        get_inventory, update_inventory,
        create_emergency_alert, get_emergency_alerts, update_emergency_alert
    )
"""

import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from datetime import datetime

# Configuration
AWS_REGION = 'us-east-1'

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
users_table = dynamodb.Table('bloodbridge_users')
requests_table = dynamodb.Table('bloodbridge_requests')
inventory_table = dynamodb.Table('bloodbridge_inventory')


# USER OPERATIONS


def create_user(user_data):
    """
    Create a new user in DynamoDB.
    
    Args:
        user_data (dict): User information including:
            - user_id (str): UUID
            - full_name (str)
            - email (str)
            - password_hash (str)
            - blood_group (str)
            - created_at (str): ISO timestamp
    
    Returns:
        bool: True if successful
    """
    try:
        users_table.put_item(
            Item=user_data,
            ConditionExpression='attribute_not_exists(user_id)'
        )
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
            raise ValueError("User already exists")
        raise


def get_user_by_id(user_id):
    """
    Get user by primary key (user_id).
    
    Args:
        user_id (str): User's UUID
    
    Returns:
        dict or None: User data
    """
    try:
        response = users_table.get_item(Key={'user_id': user_id})
        return response.get('Item')
    except ClientError:
        return None


def get_user_by_email(email):
    """
    Get user by email using Global Secondary Index.
    Used for login authentication.
    
    Args:
        email (str): User's email address
    
    Returns:
        dict or None: User data
    """
    try:
        response = users_table.query(
            IndexName='email-index',
            KeyConditionExpression=Key('email').eq(email.lower())
        )
        items = response.get('Items', [])
        return items[0] if items else None
    except ClientError:
        return None


def get_user_by_phone(phone):
    """
    Get user by phone number using Global Secondary Index.
    Used for registration verification.
    
    Args:
        phone (str): User's phone number
    
    Returns:
        dict or None: User data
    """
    try:
        # Clean phone number for comparison
        cleaned_phone = re.sub(r'[\s\-\(\)\.\+]', '', phone)
        
        # Since DynamoDB doesn't have a built-in phone GSI in our setup,
        # we'll scan for the phone number (not ideal for production)
        # In a real production scenario, you'd create a GSI for phone numbers
        response = users_table.scan(
            FilterExpression=Attr('phone').contains(cleaned_phone[-10:])  # Last 10 digits for matching
        )
        items = response.get('Items', [])
        return items[0] if items else None
    except ClientError:
        return None


def update_user(user_id, updates):
    """
    Update user attributes.
    
    Args:
        user_id (str): User's UUID
        updates (dict): Attributes to update
    
    Returns:
        bool: True if successful
    """
    try:
        update_expr = 'SET '
        expr_values = {}
        expr_names = {}
        
        for key, value in updates.items():
            safe_key = f'#{key}'
            expr_names[safe_key] = key
            expr_values[f':{key}'] = value
            update_expr += f'{safe_key} = :{key}, '
        
        update_expr = update_expr.rstrip(', ')
        
        users_table.update_item(
            Key={'user_id': user_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values
        )
        return True
    except ClientError:
        return False



# BLOOD REQUEST OPERATIONS


def create_request(request_data):
    """
    Create a new blood request.
    
    Args:
        request_data (dict): Request information including:
            - request_id (str): UUID
            - requester_id (str): User's UUID
            - blood_group (str)
            - location (str)
            - quantity (int)
            - urgency (str): low/medium/high/critical
            - status (str): pending/accepted/donated
            - created_at (str): ISO timestamp
    
    Returns:
        bool: True if successful
    """
    try:
        requests_table.put_item(Item=request_data)
        return True
    except ClientError:
        return False


def get_request_by_id(request_id):
    """
    Get blood request by ID.
    
    Args:
        request_id (str): Request UUID
    
    Returns:
        dict or None: Request data
    """
    try:
        response = requests_table.get_item(Key={'request_id': request_id})
        return response.get('Item')
    except ClientError:
        return None


def get_pending_requests():
    """
    Get all pending blood requests.
    Uses status GSI for efficient querying.
    
    Returns:
        list: List of pending requests
    """
    try:
        response = requests_table.query(
            IndexName='status-index',
            KeyConditionExpression=Key('status').eq('pending')
        )
        return response.get('Items', [])
    except ClientError:
        return []


def get_requests_by_user(user_id):
    """
    Get all requests made by a specific user.
    
    Args:
        user_id (str): User's UUID
    
    Returns:
        list: List of user's requests
    """
    try:
        response = requests_table.query(
            IndexName='requester-index',
            KeyConditionExpression=Key('requester_id').eq(user_id)
        )
        return response.get('Items', [])
    except ClientError:
        return []


def get_compatible_requests(blood_group):
    """
    Get pending requests compatible with donor's blood group.
    
    Args:
        blood_group (str): Donor's blood group
    
    Returns:
        list: List of compatible pending requests
    """
    # Blood compatibility chart
    compatibility = {
        'O-': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
        'O+': ['A+', 'B+', 'AB+', 'O+'],
        'A-': ['A+', 'A-', 'AB+', 'AB-'],
        'A+': ['A+', 'AB+'],
        'B-': ['B+', 'B-', 'AB+', 'AB-'],
        'B+': ['B+', 'AB+'],
        'AB-': ['AB+', 'AB-'],
        'AB+': ['AB+']
    }
    
    can_donate_to = compatibility.get(blood_group, [])
    pending = get_pending_requests()
    
    return [r for r in pending if r['blood_group'] in can_donate_to]


def update_request_status(request_id, status, donor_id=None):
    """
    Update blood request status.
    
    Args:
        request_id (str): Request UUID
        status (str): New status (pending/accepted/donated/cancelled)
        donor_id (str, optional): Donor's UUID
    
    Returns:
        bool: True if successful
    """
    try:
        update_expr = 'SET #status = :status, updated_at = :updated'
        expr_values = {
            ':status': status,
            ':updated': datetime.now().isoformat()
        }
        expr_names = {'#status': 'status'}
        
        if donor_id:
            update_expr += ', donor_id = :donor'
            expr_values[':donor'] = donor_id
        
        if status == 'donated':
            update_expr += ', donated_at = :donated'
            expr_values[':donated'] = datetime.now().isoformat()
        
        requests_table.update_item(
            Key={'request_id': request_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values
        )
        return True
    except ClientError:
        return False


def delete_request(request_id):
    """
    Delete a blood request.
    
    Args:
        request_id (str): Request UUID
    
    Returns:
        bool: True if successful
    """
    try:
        requests_table.delete_item(Key={'request_id': request_id})
        return True
    except ClientError:
        return False


# BLOOD REQUEST OPERATIONS (Additional Functions)


def create_blood_request(request_data):
    """
    Create a new blood request in DynamoDB.
    
    Args:
        request_data (dict): Request information including:
            - request_id (str): UUID
            - requester_id (str): User's UUID
            - blood_group (str)
            - location (str)
            - quantity (int)
            - urgency (str): low/medium/high/critical
            - status (str): pending/accepted/donated
            - created_at (str): ISO timestamp
    
    Returns:
        bool: True if successful
    """
    try:
        requests_table.put_item(Item=request_data)
        return True
    except ClientError:
        return False


def get_blood_request(request_id):
    """
    Get blood request by ID.
    
    Args:
        request_id (str): Request UUID
    
    Returns:
        dict or None: Request data
    """
    try:
        response = requests_table.get_item(Key={'request_id': request_id})
        return response.get('Item')
    except ClientError:
        return None


def update_blood_request(request_data):
    """
    Update blood request in DynamoDB.
    
    Args:
        request_data (dict): Updated request data with request_id
    
    Returns:
        bool: True if successful
    """
    try:
        request_id = request_data.get('request_id')
        update_expr = 'SET '
        expr_values = {}
        expr_names = {}
        
        # Build update expression excluding request_id (the key)
        for key, value in request_data.items():
            if key != 'request_id':
                safe_key = f'#{key}'
                expr_names[safe_key] = key
                expr_values[f':{key}'] = value
                update_expr += f'{safe_key} = :{key}, '
        
        update_expr = update_expr.rstrip(', ')
        
        requests_table.update_item(
            Key={'request_id': request_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values
        )
        return True
    except ClientError:
        return False


def get_user_blood_requests(user_id):
    """
    Get all blood requests for a specific user (both as requester and donor).
    
    Args:
        user_id (str): User's UUID
    
    Returns:
        list: List of user's requests
    """
    try:
        # Query by requester_id
        response = requests_table.query(
            IndexName='requester-index',
            KeyConditionExpression=Key('requester_id').eq(user_id)
        )
        return response.get('Items', [])
    except ClientError:
        return []


def get_all_pending_requests():
    """
    Get all pending blood requests.
    
    Returns:
        list: List of pending requests
    """
    try:
        response = requests_table.scan(
            FilterExpression=Attr('status').eq('pending')
        )
        return response.get('Items', [])
    except ClientError:
        return []


# BLOOD INVENTORY OPERATIONS


def get_inventory():
    """
    Get current blood inventory.
    
    Returns:
        dict: Blood inventory {blood_type: {units, status}}
    """
    try:
        response = inventory_table.scan()
        items = response.get('Items', [])
        
        inventory = {}
        for item in items:
            blood_type = item['blood_type']
            units = int(item.get('units', 0))
            
            # Determine status based on units
            if units <= 5:
                status = 'critical'
            elif units <= 15:
                status = 'low'
            elif units <= 25:
                status = 'moderate'
            else:
                status = 'sufficient'
            
            inventory[blood_type] = {
                'units': units,
                'status': status,
                'last_updated': item.get('last_updated')
            }
        
        return inventory
    except ClientError:
        return {}


def update_inventory(blood_type, units_change):
    """
    Update blood inventory (add or remove units).
    
    Args:
        blood_type (str): Blood type (e.g., 'O+')
        units_change (int): Units to add (positive) or remove (negative)
    
    Returns:
        bool: True if successful
    """
    try:
        inventory_table.update_item(
            Key={'blood_type': blood_type},
            UpdateExpression='SET units = units + :change, last_updated = :updated',
            ExpressionAttributeValues={
                ':change': units_change,
                ':updated': datetime.now().isoformat()
            }
        )
        return True
    except ClientError:
        return False


# UTILITY FUNCTIONS


def get_donation_stats(user_id):
    """
    Get donation statistics for a user.
    
    Args:
        user_id (str): User's UUID
    
    Returns:
        dict: Statistics {donations, requests, lives_saved}
    """
    try:
        # Get requests where user was the donor
        response = requests_table.scan(
            FilterExpression=Attr('donor_id').eq(user_id) & Attr('status').eq('donated')
        )
        donations = len(response.get('Items', []))
        
        # Get user's own requests
        user_requests = get_requests_by_user(user_id)
        
        return {
            'donations': donations,
            'requests': len(user_requests),
            'lives_saved': donations * 3
        }
    except ClientError:
        return {'donations': 0, 'requests': 0, 'lives_saved': 0}


# EMERGENCY ALERT OPERATIONS


def create_emergency_alert(alert_data):
    """
    Create a new emergency alert in DynamoDB.
    
    Args:
        alert_data (dict): Alert information including:
            - alert_id (str): UUID
            - requester_id (str): User's UUID
            - blood_group (str)
            - location (str)
            - hospital (str)
            - status (str): active/inactive
            - created_at (str): ISO timestamp
    
    Returns:
        bool: True if successful
    """
    # For now, we'll just return True since the app currently uses a local list for emergencies
    # In a real implementation, we'd create a separate table for emergencies
    return True


def get_emergency_alerts():
    """
    Get all emergency alerts.
    
    Returns:
        list: List of emergency alerts
    """
    # For now, return empty list since we don't have an emergency table set up
    # In a real implementation, we'd query an emergency alerts table
    return []


def update_emergency_alert(alert_data):
    """
    Update an emergency alert in DynamoDB.
    
    Args:
        alert_data (dict): Updated alert data with alert_id
    
    Returns:
        bool: True if successful
    """
    # For now, return True since we don't have an emergency table set up
    # In a real implementation, we'd update the emergency alerts table
    return True
