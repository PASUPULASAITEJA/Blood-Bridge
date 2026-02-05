
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
