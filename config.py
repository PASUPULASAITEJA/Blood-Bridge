"""
BloodBridge - Configuration Settings
=====================================
Configuration for local development and AWS deployment.

Usage:
    from config import get_config
    config = get_config()
"""

import os

# ENVIRONMENT DETECTION

def get_environment():
    """Detect current environment."""
    return os.environ.get('FLASK_ENV', 'development').lower()


# CONFIGURATION CLASSES

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'bloodbridge-dev-secret-key-2024')
    DEBUG = False
    TESTING = False
    
    # Application settings
    APP_NAME = 'BloodBridge'
    APP_VERSION = '1.0.0'


class DevelopmentConfig(Config):
    """Local development configuration."""
    DEBUG = True
    
    # Use local storage (Python lists/dicts)
    USE_DYNAMODB = False
    USE_SNS = False
    
    # Server settings
    HOST = '127.0.0.1'
    PORT = 5000


class ProductionConfig(Config):
    """Production/AWS configuration."""
    DEBUG = False
    
    # Use AWS services
    USE_DYNAMODB = True
    USE_SNS = True
    
    # AWS Settings
    AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
    AWS_PROFILE = os.environ.get('AWS_PROFILE', 'default')
    
    # DynamoDB Tables
    DYNAMODB_USERS_TABLE = os.environ.get('DYNAMODB_USERS_TABLE', 'bloodbridge_users')
    DYNAMODB_REQUESTS_TABLE = os.environ.get('DYNAMODB_REQUESTS_TABLE', 'bloodbridge_requests')
    DYNAMODB_INVENTORY_TABLE = os.environ.get('DYNAMODB_INVENTORY_TABLE', 'bloodbridge_inventory')
    DYNAMODB_EMERGENCIES_TABLE = os.environ.get('DYNAMODB_EMERGENCIES_TABLE', 'bloodbridge_emergencies')
    
    # SNS Configuration
    SNS_ENABLED = os.environ.get('SNS_ENABLED', 'true').lower() == 'true'
    SNS_ALERTS_TOPIC = os.environ.get('SNS_ALERTS_TOPIC', '')
    SNS_EMERGENCY_TOPIC = os.environ.get('SNS_EMERGENCY_TOPIC', '')
    SNS_REGION = os.environ.get('SNS_REGION', 'us-east-1')
    
    # CloudWatch Logging
    CLOUDWATCH_LOG_GROUP = os.environ.get('CLOUDWATCH_LOG_GROUP', '/aws/bloodbridge/app')
    CLOUDWATCH_ENABLED = os.environ.get('CLOUDWATCH_ENABLED', 'true').lower() == 'true'
    
    # Server settings
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 80))
    WORKERS = int(os.environ.get('WORKERS', 4))
    
    # Security - Must set in environment!
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    def __init__(self):
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable must be set in production!")


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    
    USE_DYNAMODB = False
    USE_SNS = False


# CONFIGURATION SELECTOR

config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}


def get_config():
    """Get configuration based on environment."""
    env = get_environment()
    config_class = config_map.get(env, DevelopmentConfig)
    return config_class()


# BLOOD GROUP CONSTANTS

BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

# Who can DONATE to whom
COMPATIBILITY = {
    'O-':  ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],  # Universal donor
    'O+':  ['A+', 'B+', 'AB+', 'O+'],
    'A-':  ['A+', 'A-', 'AB+', 'AB-'],
    'A+':  ['A+', 'AB+'],
    'B-':  ['B+', 'B-', 'AB+', 'AB-'],
    'B+':  ['B+', 'AB+'],
    'AB-': ['AB+', 'AB-'],
    'AB+': ['AB+']  # Can only donate to AB+
}

# Who can RECEIVE from whom
CAN_RECEIVE_FROM = {
    'O-':  ['O-'],  # Can only receive from O-
    'O+':  ['O-', 'O+'],
    'A-':  ['O-', 'A-'],
    'A+':  ['O-', 'O+', 'A-', 'A+'],
    'B-':  ['O-', 'B-'],
    'B+':  ['O-', 'O+', 'B-', 'B+'],
    'AB-': ['O-', 'A-', 'B-', 'AB-'],
    'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+']  # Universal recipient
}


# BADGE DEFINITIONS

BADGES = {
    'first_blood': {
        'name': 'First Blood',
        'icon': '🩸',
        'description': 'Made your first donation'
    },
    'lifesaver_3': {
        'name': 'Lifesaver',
        'icon': '💖',
        'description': 'Saved 3 lives (1 donation = 3 lives)'
    },
    'hero': {
        'name': 'Hero',
        'icon': '🦸',
        'description': 'Made 5+ donations'
    },
    'emergency_responder': {
        'name': 'Emergency Responder',
        'icon': '🚨',
        'description': 'Responded to an emergency'
    },
    'rare_donor': {
        'name': 'Rare Donor',
        'icon': '💎',
        'description': 'Donated rare blood type (AB-, B-, O-)'
    }
}


# URGENCY LEVELS

URGENCY_LEVELS = {
    'low': {'label': 'Low', 'color': 'green', 'description': 'Within a week'},
    'medium': {'label': 'Medium', 'color': 'yellow', 'description': 'Within 3 days'},
    'high': {'label': 'High', 'color': 'orange', 'description': 'Within 24 hours'},
    'critical': {'label': 'Critical', 'color': 'red', 'description': 'Immediate'}
}
