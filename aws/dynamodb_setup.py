"""
BloodBridge - DynamoDB Table Setup Script
==========================================
This script creates the required DynamoDB tables for BloodBridge.

Prerequisites:
1. AWS CLI configured with credentials
2. boto3 installed (pip install boto3)

Usage:
    python aws/dynamodb_setup.py

Tables Created:
1. bloodbridge_users - User accounts
2. bloodbridge_requests - Blood requests
3. bloodbridge_inventory - Blood inventory
"""

import boto3
from botocore.exceptions import ClientError

# Configuration
AWS_REGION = 'us-east-1'  # Change as needed

def create_users_table(dynamodb):
    """
    Create the users table with email GSI for login queries.
    
    Schema:
    - user_id (PK): Unique identifier
    - email (GSI): For login lookups
    - full_name, password_hash, blood_group, created_at
    """
    try:
        table = dynamodb.create_table(
            TableName='bloodbridge_users',
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'email', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'email-index',
                    'KeySchema': [
                        {'AttributeName': 'email', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.wait_until_exists()
        print("✅ Table 'bloodbridge_users' created successfully!")
        return table
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("⚠️  Table 'bloodbridge_users' already exists.")
        else:
            raise


def create_requests_table(dynamodb):
    """
    Create the blood requests table with status GSI.
    
    Schema:
    - request_id (PK): Unique identifier
    - status (GSI): For filtering pending/accepted/donated
    - requester_id, blood_group, location, quantity, urgency, donor_id
    """
    try:
        table = dynamodb.create_table(
            TableName='bloodbridge_requests',
            KeySchema=[
                {'AttributeName': 'request_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'request_id', 'AttributeType': 'S'},
                {'AttributeName': 'status', 'AttributeType': 'S'},
                {'AttributeName': 'requester_id', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'status-index',
                    'KeySchema': [
                        {'AttributeName': 'status', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                },
                {
                    'IndexName': 'requester-index',
                    'KeySchema': [
                        {'AttributeName': 'requester_id', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.wait_until_exists()
        print("✅ Table 'bloodbridge_requests' created successfully!")
        return table
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("⚠️  Table 'bloodbridge_requests' already exists.")
        else:
            raise


def create_inventory_table(dynamodb):
    """
    Create the blood inventory table.
    
    Schema:
    - blood_type (PK): A+, A-, B+, B-, AB+, AB-, O+, O-
    - units: Available units
    - last_updated: Timestamp
    """
    try:
        table = dynamodb.create_table(
            TableName='bloodbridge_inventory',
            KeySchema=[
                {'AttributeName': 'blood_type', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'blood_type', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table.wait_until_exists()
        print("✅ Table 'bloodbridge_inventory' created successfully!")
        
        # Initialize with default inventory
        init_inventory(table)
        return table
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("⚠️  Table 'bloodbridge_inventory' already exists.")
        else:
            raise


def init_inventory(table):
    """Initialize blood inventory with default values."""
    from datetime import datetime
    
    blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    default_units = {'A+': 25, 'A-': 12, 'B+': 18, 'B-': 8, 
                     'AB+': 15, 'AB-': 5, 'O+': 30, 'O-': 10}
    
    for bt in blood_types:
        table.put_item(Item={
            'blood_type': bt,
            'units': default_units[bt],
            'last_updated': datetime.now().isoformat()
        })
    print("✅ Blood inventory initialized!")


def main():
    """Main function to create all tables."""
    print("\n" + "="*50)
    print("  BloodBridge - DynamoDB Setup")
    print("="*50 + "\n")
    
    # Initialize DynamoDB resource
    dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
    
    print(f"Region: {AWS_REGION}\n")
    print("Creating tables...\n")
    
    # Create tables
    create_users_table(dynamodb)
    create_requests_table(dynamodb)
    create_inventory_table(dynamodb)
    
    print("\n" + "="*50)
    print("  Setup Complete!")
    print("="*50 + "\n")


if __name__ == '__main__':
    main()
