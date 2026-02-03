"""
BloodBridge - DynamoDB Table Setup Script
========================================
This script creates the required DynamoDB tables for BloodBridge.

Prerequisites:
1. AWS CLI configured with credentials
2. boto3 installed (pip install boto3)

Usage:
    python aws/dynamodb_setup.py

Tables Created:
1. bloodbridge_users
2. bloodbridge_requests
3. bloodbridge_inventory
"""

import os
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

# CONFIGURATION

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")


# USERS TABLE

def create_users_table(dynamodb):
    """
    Table: bloodbridge_users
    PK : user_id
    GSI: email-index (email)
    """
    try:
        table = dynamodb.create_table(
            TableName="bloodbridge_users",
            KeySchema=[
                {"AttributeName": "user_id", "KeyType": "HASH"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "email", "AttributeType": "S"}
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "email-index",
                    "KeySchema": [
                        {"AttributeName": "email", "KeyType": "HASH"}
                    ],
                    "Projection": {"ProjectionType": "ALL"}
                }
            ],
            BillingMode="PAY_PER_REQUEST"
        )
        table.wait_until_exists()
        print("✅ Table created: bloodbridge_users")
        return table

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print("⚠️  Table already exists: bloodbridge_users")
        else:
            raise

# REQUESTS TABLE

def create_requests_table(dynamodb):
    """
    Table: bloodbridge_requests
    PK : request_id
    GSI: status-index (status)
    GSI: requester-index (requester_id)
    """
    try:
        table = dynamodb.create_table(
            TableName="bloodbridge_requests",
            KeySchema=[
                {"AttributeName": "request_id", "KeyType": "HASH"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "request_id", "AttributeType": "S"},
                {"AttributeName": "status", "AttributeType": "S"},
                {"AttributeName": "requester_id", "AttributeType": "S"}
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "status-index",
                    "KeySchema": [
                        {"AttributeName": "status", "KeyType": "HASH"}
                    ],
                    "Projection": {"ProjectionType": "ALL"}
                },
                {
                    "IndexName": "requester-index",
                    "KeySchema": [
                        {"AttributeName": "requester_id", "KeyType": "HASH"}
                    ],
                    "Projection": {"ProjectionType": "ALL"}
                }
            ],
            BillingMode="PAY_PER_REQUEST"
        )
        table.wait_until_exists()
        print("✅ Table created: bloodbridge_requests")
        return table

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print("⚠️  Table already exists: bloodbridge_requests")
        else:
            raise


# INVENTORY TABLE

def create_inventory_table(dynamodb):
    """
    Table: bloodbridge_inventory
    PK : blood_type
    """
    try:
        table = dynamodb.create_table(
            TableName="bloodbridge_inventory",
            KeySchema=[
                {"AttributeName": "blood_type", "KeyType": "HASH"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "blood_type", "AttributeType": "S"}
            ],
            BillingMode="PAY_PER_REQUEST"
        )
        table.wait_until_exists()
        print("✅ Table created: bloodbridge_inventory")

        initialize_inventory(table)
        return table

    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceInUseException":
            print("⚠️  Table already exists: bloodbridge_inventory")
        else:
            raise


# INVENTORY INITIALIZATION

def initialize_inventory(table):
    """Insert default blood inventory values."""
    default_inventory = {
        "A+": 25, "A-": 12,
        "B+": 18, "B-": 8,
        "AB+": 15, "AB-": 5,
        "O+": 30, "O-": 10
    }

    for blood_type, units in default_inventory.items():
        table.put_item(
            Item={
                "blood_type": blood_type,
                "units": units,
                "last_updated": datetime.now().isoformat()
            }
        )

    print("✅ Blood inventory initialized")

# MAIN

def main():
    print("\n" + "=" * 55)
    print("   BloodBridge – DynamoDB Setup")
    print("=" * 55)

    print(f"Region: {AWS_REGION}\n")

    dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)

    print("Creating DynamoDB tables...\n")

    create_users_table(dynamodb)
    create_requests_table(dynamodb)
    create_inventory_table(dynamodb)

    print("\n" + "=" * 55)
    print("   DynamoDB Setup Completed Successfully")
    print("=" * 55 + "\n")

# -------------------------------------------------
if __name__ == "__main__":
    main()
