"""
BloodBridge - Configuration Settings
=====================================
This file contains all configuration settings for the application.
Modify these settings for different environments (local, dev, prod).
"""

import os

# ============================================
# FLASK SETTINGS
# ============================================

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bloodbridge-secret-key-change-in-production'
    DEBUG = False
    TESTING = False


class LocalConfig(Config):
    """Local development configuration (no AWS)."""
    DEBUG = True
    USE_AWS = False
    
    # Local storage (Python lists/dicts)
    STORAGE_TYPE = 'local'


class AWSConfig(Config):
    """AWS deployment configuration."""
    DEBUG = False
    USE_AWS = True
    
    # AWS Settings
    AWS_REGION = os.environ.get('AWS_REGION') or 'us-east-1'
    
    # DynamoDB Tables
    DYNAMODB_USERS_TABLE = 'bloodbridge_users'
    DYNAMODB_REQUESTS_TABLE = 'bloodbridge_requests'
    DYNAMODB_INVENTORY_TABLE = 'bloodbridge_inventory'
    
    # SNS Topics
    SNS_ALERTS_TOPIC = os.environ.get('SNS_ALERTS_TOPIC') or 'arn:aws:sns:us-east-1:YOUR_ACCOUNT:bloodbridge-alerts'
    SNS_EMERGENCY_TOPIC = os.environ.get('SNS_EMERGENCY_TOPIC') or 'arn:aws:sns:us-east-1:YOUR_ACCOUNT:bloodbridge-emergency'


class ProductionConfig(AWSConfig):
    """Production configuration."""
    DEBUG = False
    
    # Use environment variable for secret key in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for production!")


# ============================================
# BLOOD GROUP SETTINGS
# ============================================

BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

# Blood compatibility chart
# Key: Donor blood type → Value: Can donate to these types
BLOOD_COMPATIBILITY = {
    'O-':  ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],  # Universal donor
    'O+':  ['A+', 'B+', 'AB+', 'O+'],
    'A-':  ['A+', 'A-', 'AB+', 'AB-'],
    'A+':  ['A+', 'AB+'],
    'B-':  ['B+', 'B-', 'AB+', 'AB-'],
    'B+':  ['B+', 'AB+'],
    'AB-': ['AB+', 'AB-'],
    'AB+': ['AB+']  # Can only donate to AB+
}

# Can receive from
BLOOD_RECEIVE_FROM = {
    'O-':  ['O-'],  # Can only receive from O-
    'O+':  ['O-', 'O+'],
    'A-':  ['O-', 'A-'],
    'A+':  ['O-', 'O+', 'A-', 'A+'],
    'B-':  ['O-', 'B-'],
    'B+':  ['O-', 'O+', 'B-', 'B+'],
    'AB-': ['O-', 'A-', 'B-', 'AB-'],
    'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+']  # Universal recipient
}


# ============================================
# URGENCY SETTINGS
# ============================================

URGENCY_LEVELS = ['low', 'medium', 'high', 'critical']

URGENCY_DESCRIPTIONS = {
    'low': 'Within a week',
    'medium': 'Within 3 days',
    'high': 'Within 24 hours',
    'critical': 'Immediate'
}


# ============================================
# BADGE SYSTEM
# ============================================

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
    },
    'regular': {
        'name': 'Regular Donor',
        'icon': '⭐',
        'description': 'Donated 3+ times'
    },
    'champion': {
        'name': 'Champion',
        'icon': '🏆',
        'description': 'Made 10+ donations'
    }
}


# ============================================
# CONFIGURATION SELECTOR
# ============================================

def get_config():
    """
    Get configuration based on environment.
    Set FLASK_ENV environment variable to switch:
    - 'local' or 'development': LocalConfig
    - 'aws': AWSConfig
    - 'production': ProductionConfig
    """
    env = os.environ.get('FLASK_ENV', 'local').lower()
    
    configs = {
        'local': LocalConfig,
        'development': LocalConfig,
        'aws': AWSConfig,
        'production': ProductionConfig
    }
    
    return configs.get(env, LocalConfig)
