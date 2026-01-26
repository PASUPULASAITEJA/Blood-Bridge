# BloodBridge – Optimizing Lifesaving Resources Using AWS Services
## Complete Development Guide for Final Year Project

---

# Table of Contents

1. [Project Overview](#1-project-overview)
2. [Project Folder Structure](#2-project-folder-structure)
3. [Flask App Initialization](#3-flask-app-initialization)
4. [User Registration & Login Module](#4-user-registration--login-module)
5. [Dashboard Implementation](#5-dashboard-implementation)
6. [Blood Request Submission](#6-blood-request-submission)
7. [Donor Response & Confirmation](#7-donor-response--confirmation)
8. [Local Testing & Validation](#8-local-testing--validation)
9. [DynamoDB Table Design](#9-dynamodb-table-design)
10. [Replacing Local Storage with DynamoDB](#10-replacing-local-storage-with-dynamodb)
11. [SNS Integration](#11-sns-integration)
12. [IAM Role Usage](#12-iam-role-usage)
13. [EC2 Deployment](#13-ec2-deployment)
14. [Running Flask on Port 80](#14-running-flask-on-port-80)
15. [Testing Guide](#15-testing-guide)
16. [Common Errors & Fixes](#16-common-errors--fixes)
17. [Viva Questions & Answers](#17-viva-questions--answers)
18. [Future Enhancements](#18-future-enhancements)

---

# 1. Project Overview

## 1.1 What is BloodBridge?

BloodBridge is a web-based blood bank management system that connects blood donors with recipients in real-time. It optimizes the process of finding compatible blood donors during emergencies.

## 1.2 Problem Statement

- Blood shortages cause preventable deaths
- No centralized system to find compatible donors quickly
- Manual processes delay emergency responses
- Lack of real-time notifications for urgent requests

## 1.3 Solution

BloodBridge provides:
- Real-time donor-recipient matching based on blood compatibility
- Emergency SOS alerts to all compatible donors
- Live blood inventory tracking
- Instant notifications via AWS SNS

## 1.4 Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Python Flask |
| Frontend | HTML, CSS, Jinja2 Templates |
| Database | AWS DynamoDB (NoSQL) |
| Notifications | AWS SNS |
| Hosting | AWS EC2 |
| Authentication | Flask Sessions |
| SDK | boto3 (AWS SDK for Python) |

## 1.5 Development Approach

```
Phase 1: Local Development (Python lists/dictionaries)
    ↓
Phase 2: AWS Integration (DynamoDB, SNS)
    ↓
Phase 3: Cloud Deployment (EC2)
```

---

# 2. Project Folder Structure

## 2.1 Standard Flask Project Structure

```
bloodbridge/
│
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── DEVELOPMENT_GUIDE.md        # This guide
│
├── templates/                  # HTML templates (Jinja2)
│   ├── base.html              # Base template with navigation
│   ├── index.html             # Landing page
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   ├── dashboard.html         # User dashboard
│   ├── create_request.html    # Create blood request
│   ├── all_requests.html      # View all requests
│   ├── profile.html           # User profile
│   ├── realtime_dashboard.html # Real-time monitoring
│   ├── blood_inventory.html   # Blood stock levels
│   ├── blood_camps.html       # Donation camps
│   ├── sos_emergency.html     # Emergency SOS
│   ├── emergency_list.html    # Emergency alerts
│   ├── leaderboard.html       # Donor rankings
│   └── error.html             # Error pages
│
├── static/                     # Static files (optional)
│   ├── css/
│   ├── js/
│   └── images/
│
└── aws/                        # AWS integration (Phase 2)
    ├── dynamodb_setup.py      # DynamoDB table creation
    ├── sns_setup.py           # SNS topic setup
    └── iam_policy.json        # IAM policy document
```

## 2.2 Why This Structure?

| Folder/File | Purpose |
|-------------|---------|
| `app.py` | Single entry point for Flask application |
| `templates/` | Jinja2 templates for server-side rendering |
| `static/` | CSS, JS, images (we use Tailwind CDN instead) |
| `config.py` | Separates configuration from code |
| `aws/` | AWS-specific setup scripts |

---

# 3. Flask App Initialization

## 3.1 Installing Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install flask werkzeug boto3
```

## 3.2 Basic Flask App Structure

```python
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import uuid
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Run the app
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
```

## 3.3 Session Handling Explained

**What is a Session?**
A session stores user data across multiple HTTP requests. Flask uses cookies to maintain session state.

```python
# Setting session data (on login)
session['user_id'] = user['user_id']
session['user_name'] = user['full_name']
session['blood_group'] = user['blood_group']

# Accessing session data
current_user = session.get('user_id')

# Clearing session (on logout)
session.clear()
```

## 3.4 Login Required Decorator

```python
def login_required(f):
    """
    Decorator to protect routes that require authentication.
    Redirects to login page if user is not logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Usage:
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')
```

---

# 4. User Registration & Login Module

## 4.1 Data Structure for Users (Local Storage)

```python
# In-memory storage (will be replaced by DynamoDB)
users_db = []

# User schema
user = {
    'user_id': 'uuid-string',      # Primary Key
    'full_name': 'John Smith',
    'email': 'john@example.com',   # Unique
    'password_hash': 'hashed...',  # Never store plain passwords
    'blood_group': 'O+',
    'created_at': '2024-01-15T10:30:00'
}
```

## 4.2 Registration Logic

```python
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        blood_group = request.form.get('blood_group', '')
        
        # Validation
        if not all([full_name, email, password, blood_group]):
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        
        # Check if email exists
        # TODO [DynamoDB]: Replace with query using GSI on email
        for user in users_db:
            if user['email'] == email:
                flash('Email already registered.', 'danger')
                return render_template('register.html')
        
        # Create new user
        # TODO [DynamoDB]: Replace with put_item()
        new_user = {
            'user_id': str(uuid.uuid4()),
            'full_name': full_name,
            'email': email,
            'password_hash': generate_password_hash(password),
            'blood_group': blood_group,
            'created_at': datetime.now().isoformat()
        }
        users_db.append(new_user)
        
        # TODO [SNS]: Send welcome email notification
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')
```

## 4.3 Login Logic

```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        # Find user by email
        # TODO [DynamoDB]: Replace with query using GSI
        user = None
        for u in users_db:
            if u['email'] == email:
                user = u
                break
        
        # Verify password
        if user and check_password_hash(user['password_hash'], password):
            # Create session
            session['user_id'] = user['user_id']
            session['user_name'] = user['full_name']
            session['blood_group'] = user['blood_group']
            
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')
```

## 4.4 Password Security

**Why Hash Passwords?**
- Plain text passwords are vulnerable to theft
- Hashing is one-way (cannot be reversed)
- Werkzeug uses PBKDF2 with SHA-256

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Hashing a password (during registration)
password_hash = generate_password_hash('user_password')
# Result: 'pbkdf2:sha256:...'

# Verifying a password (during login)
is_valid = check_password_hash(password_hash, 'user_password')
# Result: True or False
```

---

# 5. Dashboard Implementation

## 5.1 Blood Compatibility Logic

```python
# Blood compatibility chart
# Key: Donor blood type → Value: Can donate to these types
COMPATIBILITY = {
    'O-':  ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],  # Universal donor
    'O+':  ['A+', 'B+', 'AB+', 'O+'],
    'A-':  ['A+', 'A-', 'AB+', 'AB-'],
    'A+':  ['A+', 'AB+'],
    'B-':  ['B+', 'B-', 'AB+', 'AB-'],
    'B+':  ['B+', 'AB+'],
    'AB-': ['AB+', 'AB-'],
    'AB+': ['AB+']  # Universal recipient (can receive from all)
}
```

## 5.2 Finding Compatible Requests

```python
def get_compatible_requests(user_blood_group):
    """
    Find blood requests that the logged-in user can donate to.
    Based on blood group compatibility rules.
    """
    # Get list of blood types this user can donate to
    can_donate_to = COMPATIBILITY.get(user_blood_group, [])
    
    matching_requests = []
    for req in blood_requests_db:
        if req['blood_group'] in can_donate_to and req['status'] == 'pending':
            matching_requests.append(req)
    
    return matching_requests
```

## 5.3 Dashboard Route

```python
@app.route('/dashboard')
@login_required
def dashboard():
    user_blood_group = session.get('blood_group')
    
    # Get requests this user can help with
    matching_requests = get_compatible_requests(user_blood_group)
    
    # Sort by urgency (critical first)
    urgency_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    matching_requests.sort(key=lambda x: urgency_order.get(x['urgency'], 4))
    
    # Get user's own requests
    my_requests = [r for r in blood_requests_db 
                   if r['requester_id'] == session['user_id']]
    
    # Get user's donations
    my_donations = [r for r in blood_requests_db 
                    if r.get('donor_id') == session['user_id']]
    
    return render_template('dashboard.html',
        matching_requests=matching_requests,
        my_requests=my_requests,
        my_donations=my_donations,
        user_blood_group=user_blood_group
    )
```

---

# 6. Blood Request Submission

## 6.1 Blood Request Data Structure

```python
blood_requests_db = []

# Request schema
blood_request = {
    'request_id': 'uuid-string',     # Primary Key
    'requester_id': 'user-uuid',     # Foreign Key to users
    'blood_group': 'A+',
    'location': 'City Hospital',
    'quantity': 2,                    # Units needed
    'urgency': 'critical',           # low, medium, high, critical
    'notes': 'Surgery scheduled',
    'status': 'pending',             # pending, accepted, donated, cancelled
    'donor_id': None,                # Filled when donor responds
    'created_at': '2024-01-15T10:30:00',
    'donated_at': None
}
```

## 6.2 Create Request Route

```python
@app.route('/request/create', methods=['GET', 'POST'])
@login_required
def create_request():
    if request.method == 'POST':
        # Get form data
        blood_group = request.form.get('blood_group')
        location = request.form.get('location', '').strip()
        quantity = int(request.form.get('quantity', 1))
        urgency = request.form.get('urgency', 'medium')
        notes = request.form.get('notes', '').strip()
        
        # Create new request
        # TODO [DynamoDB]: Replace with put_item()
        new_request = {
            'request_id': str(uuid.uuid4()),
            'requester_id': session['user_id'],
            'blood_group': blood_group,
            'location': location,
            'quantity': quantity,
            'urgency': urgency,
            'notes': notes,
            'status': 'pending',
            'donor_id': None,
            'created_at': datetime.now().isoformat()
        }
        blood_requests_db.append(new_request)
        
        # TODO [SNS]: Notify compatible donors about new request
        # publish_to_sns(f"Blood Request: {blood_group} needed at {location}")
        
        flash('Blood request created successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('create_request.html')
```

---

# 7. Donor Response & Confirmation

## 7.1 Workflow Diagram

```
[Request Created] → [Pending]
        ↓
[Donor Responds] → [Accepted]
        ↓
[Requester Confirms] → [Donated]
```

## 7.2 Donor Response Route

```python
@app.route('/request/<request_id>/respond', methods=['POST'])
@login_required
def respond_to_request(request_id):
    # Find the request
    # TODO [DynamoDB]: Replace with get_item()
    blood_request = None
    for req in blood_requests_db:
        if req['request_id'] == request_id:
            blood_request = req
            break
    
    if not blood_request:
        flash('Request not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Validation
    if blood_request['status'] != 'pending':
        flash('This request is no longer available.', 'warning')
        return redirect(url_for('dashboard'))
    
    if blood_request['requester_id'] == session['user_id']:
        flash('You cannot respond to your own request.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Update request status
    # TODO [DynamoDB]: Replace with update_item()
    blood_request['status'] = 'accepted'
    blood_request['donor_id'] = session['user_id']
    blood_request['accepted_at'] = datetime.now().isoformat()
    
    # TODO [SNS]: Notify requester that donor found
    
    flash('Thank you for offering to donate!', 'success')
    return redirect(url_for('dashboard'))
```

## 7.3 Confirm Donation Route

```python
@app.route('/request/<request_id>/confirm', methods=['POST'])
@login_required
def confirm_donation(request_id):
    # Find the request
    blood_request = None
    for req in blood_requests_db:
        if req['request_id'] == request_id:
            blood_request = req
            break
    
    if not blood_request:
        flash('Request not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Only requester can confirm
    if blood_request['requester_id'] != session['user_id']:
        flash('Only the requester can confirm donation.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Update status to donated
    # TODO [DynamoDB]: Replace with update_item()
    blood_request['status'] = 'donated'
    blood_request['donated_at'] = datetime.now().isoformat()
    
    # TODO [SNS]: Send thank you notification to donor
    
    flash('Donation confirmed! Thank you!', 'success')
    return redirect(url_for('dashboard'))
```

---

# 8. Local Testing & Validation

## 8.1 Running the Application

```bash
# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run Flask app
python app.py

# Output:
# * Running on http://127.0.0.1:5000
```

## 8.2 Test Cases

| Test Case | Steps | Expected Result |
|-----------|-------|-----------------|
| Registration | Fill form, submit | User created, redirect to login |
| Duplicate Email | Register with existing email | Error message shown |
| Login | Enter valid credentials | Redirect to dashboard |
| Invalid Login | Enter wrong password | Error message shown |
| Create Request | Fill request form, submit | Request appears on dashboard |
| Respond to Request | Click "Donate" button | Status changes to "accepted" |
| Confirm Donation | Requester clicks "Confirm" | Status changes to "donated" |
| Logout | Click logout | Session cleared, redirect to home |

## 8.3 Demo Data for Testing

```python
def seed_demo_data():
    """Create demo data for testing."""
    # Demo users
    demo_users = [
        {'name': 'John Smith', 'email': 'john@demo.com', 
         'blood': 'O+', 'password': 'demo123'},
        {'name': 'Sarah Johnson', 'email': 'sarah@demo.com', 
         'blood': 'A+', 'password': 'demo123'},
    ]
    
    for user in demo_users:
        users_db.append({
            'user_id': str(uuid.uuid4()),
            'full_name': user['name'],
            'email': user['email'],
            'password_hash': generate_password_hash(user['password']),
            'blood_group': user['blood'],
            'created_at': datetime.now().isoformat()
        })
```

---

# 9. DynamoDB Table Design

## 9.1 What is DynamoDB?

DynamoDB is a fully managed NoSQL database service by AWS that provides:
- Fast performance at any scale
- Automatic scaling
- Built-in security
- No server management

## 9.2 Table: bloodbridge_users

| Attribute | Type | Description |
|-----------|------|-------------|
| `user_id` | String (PK) | Primary Key (UUID) |
| `email` | String (GSI) | Global Secondary Index for login |
| `full_name` | String | User's full name |
| `password_hash` | String | Hashed password |
| `blood_group` | String | Blood type |
| `created_at` | String | ISO timestamp |

**GSI (Global Secondary Index):** Allows querying by email instead of user_id

## 9.3 Table: bloodbridge_requests

| Attribute | Type | Description |
|-----------|------|-------------|
| `request_id` | String (PK) | Primary Key (UUID) |
| `requester_id` | String (GSI) | To find user's requests |
| `blood_group` | String | Blood type needed |
| `location` | String | Hospital/location |
| `quantity` | Number | Units needed |
| `urgency` | String | low/medium/high/critical |
| `status` | String (GSI) | pending/accepted/donated |
| `donor_id` | String | Donor's user_id |
| `created_at` | String | ISO timestamp |

## 9.4 DynamoDB Setup Script

```python
# aws/dynamodb_setup.py
import boto3

def create_tables():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    
    # Create Users Table
    users_table = dynamodb.create_table(
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
    
    # Create Requests Table
    requests_table = dynamodb.create_table(
        TableName='bloodbridge_requests',
        KeySchema=[
            {'AttributeName': 'request_id', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'request_id', 'AttributeType': 'S'},
            {'AttributeName': 'status', 'AttributeType': 'S'}
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
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    
    print("Tables created successfully!")

if __name__ == '__main__':
    create_tables()
```

---

# 10. Replacing Local Storage with DynamoDB

## 10.1 Install boto3

```bash
pip install boto3
```

## 10.2 Configure AWS Credentials

```bash
# Option 1: AWS CLI
aws configure
# Enter: Access Key ID, Secret Key, Region

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

## 10.3 DynamoDB Helper Functions

```python
import boto3
from boto3.dynamodb.conditions import Key

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
users_table = dynamodb.Table('bloodbridge_users')
requests_table = dynamodb.Table('bloodbridge_requests')

# CREATE - Add new user
def create_user(user_data):
    """Insert a new user into DynamoDB."""
    users_table.put_item(Item=user_data)

# READ - Get user by ID
def get_user_by_id(user_id):
    """Retrieve user by primary key."""
    response = users_table.get_item(Key={'user_id': user_id})
    return response.get('Item')

# READ - Get user by email (using GSI)
def get_user_by_email(email):
    """Query user by email using Global Secondary Index."""
    response = users_table.query(
        IndexName='email-index',
        KeyConditionExpression=Key('email').eq(email)
    )
    items = response.get('Items', [])
    return items[0] if items else None

# UPDATE - Update request status
def update_request_status(request_id, status, donor_id=None):
    """Update blood request status."""
    update_expr = 'SET #status = :status'
    expr_values = {':status': status}
    expr_names = {'#status': 'status'}
    
    if donor_id:
        update_expr += ', donor_id = :donor_id'
        expr_values[':donor_id'] = donor_id
    
    requests_table.update_item(
        Key={'request_id': request_id},
        UpdateExpression=update_expr,
        ExpressionAttributeNames=expr_names,
        ExpressionAttributeValues=expr_values
    )

# DELETE - Delete a request
def delete_request(request_id):
    """Delete a blood request."""
    requests_table.delete_item(Key={'request_id': request_id})

# SCAN - Get all pending requests
def get_pending_requests():
    """Get all pending blood requests."""
    response = requests_table.query(
        IndexName='status-index',
        KeyConditionExpression=Key('status').eq('pending')
    )
    return response.get('Items', [])
```

## 10.4 Migration Example

**Before (Local Storage):**
```python
# Creating a user
new_user = {...}
users_db.append(new_user)
```

**After (DynamoDB):**
```python
# Creating a user
new_user = {...}
users_table.put_item(Item=new_user)
```

---

# 11. SNS Integration

## 11.1 What is SNS?

Amazon Simple Notification Service (SNS) is a messaging service for sending notifications:
- Push notifications to mobile devices
- SMS text messages
- Email notifications
- HTTP/HTTPS endpoints

## 11.2 SNS Setup Script

```python
# aws/sns_setup.py
import boto3

def setup_sns():
    sns = boto3.client('sns', region_name='us-east-1')
    
    # Create topic for blood requests
    response = sns.create_topic(Name='bloodbridge-alerts')
    topic_arn = response['TopicArn']
    
    print(f"Topic ARN: {topic_arn}")
    return topic_arn

if __name__ == '__main__':
    setup_sns()
```

## 11.3 SNS Helper Functions

```python
import boto3

sns = boto3.client('sns', region_name='us-east-1')
TOPIC_ARN = 'arn:aws:sns:us-east-1:123456789:bloodbridge-alerts'

def send_notification(subject, message):
    """Send notification to all subscribers."""
    sns.publish(
        TopicArn=TOPIC_ARN,
        Subject=subject,
        Message=message
    )

def send_sms(phone_number, message):
    """Send SMS to specific phone number."""
    sns.publish(
        PhoneNumber=phone_number,
        Message=message
    )

def send_email_notification(email, subject, message):
    """Send email notification."""
    # First, subscribe the email to topic
    sns.subscribe(
        TopicArn=TOPIC_ARN,
        Protocol='email',
        Endpoint=email
    )
    # Then publish
    sns.publish(
        TopicArn=TOPIC_ARN,
        Subject=subject,
        Message=message
    )
```

## 11.4 Integration Points in BloodBridge

```python
# When new blood request is created
def create_request():
    # ... create request logic ...
    
    # Send SNS notification
    send_notification(
        subject=f"URGENT: {blood_group} Blood Needed",
        message=f"Location: {location}\nUrgency: {urgency}"
    )

# When donor responds
def respond_to_request():
    # ... response logic ...
    
    # Notify requester
    send_notification(
        subject="Donor Found!",
        message=f"A donor has agreed to help with your request."
    )

# Emergency SOS
def sos_emergency():
    # ... SOS logic ...
    
    # Broadcast to all
    send_notification(
        subject="🆘 EMERGENCY BLOOD REQUEST",
        message=f"CRITICAL: {blood_group} needed immediately at {location}"
    )
```

---

# 12. IAM Role Usage

## 12.1 What is IAM?

AWS Identity and Access Management (IAM) controls:
- Who can access AWS resources (authentication)
- What actions they can perform (authorization)

## 12.2 IAM Components

| Component | Description |
|-----------|-------------|
| **User** | Individual identity with credentials |
| **Group** | Collection of users with shared permissions |
| **Role** | Temporary permissions for services |
| **Policy** | JSON document defining permissions |

## 12.3 BloodBridge IAM Policy

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DynamoDBAccess",
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": [
                "arn:aws:dynamodb:us-east-1:*:table/bloodbridge_users",
                "arn:aws:dynamodb:us-east-1:*:table/bloodbridge_requests",
                "arn:aws:dynamodb:us-east-1:*:table/*/index/*"
            ]
        },
        {
            "Sid": "SNSAccess",
            "Effect": "Allow",
            "Action": [
                "sns:Publish",
                "sns:Subscribe"
            ],
            "Resource": "arn:aws:sns:us-east-1:*:bloodbridge-*"
        }
    ]
}
```

## 12.4 Creating IAM Role for EC2

```bash
# 1. Create the role
aws iam create-role \
    --role-name BloodBridgeEC2Role \
    --assume-role-policy-document file://trust-policy.json

# 2. Attach the policy
aws iam put-role-policy \
    --role-name BloodBridgeEC2Role \
    --policy-name BloodBridgePolicy \
    --policy-document file://bloodbridge-policy.json

# 3. Create instance profile
aws iam create-instance-profile \
    --instance-profile-name BloodBridgeProfile

# 4. Add role to profile
aws iam add-role-to-instance-profile \
    --instance-profile-name BloodBridgeProfile \
    --role-name BloodBridgeEC2Role
```

---

# 13. EC2 Deployment

## 13.1 What is EC2?

Amazon Elastic Compute Cloud (EC2) provides:
- Virtual servers in the cloud
- Scalable computing capacity
- Pay-per-use pricing

## 13.2 Launch EC2 Instance

### Step 1: Choose AMI
- Select: **Amazon Linux 2023 AMI**

### Step 2: Choose Instance Type
- Select: **t2.micro** (free tier eligible)

### Step 3: Configure Security Group
```
Inbound Rules:
- SSH (22) - Your IP
- HTTP (80) - Anywhere (0.0.0.0/0)
- Custom TCP (5000) - Anywhere (for testing)
```

### Step 4: Create Key Pair
- Download .pem file
- Keep it secure

## 13.3 Connect to EC2

```bash
# Set permissions on key file
chmod 400 bloodbridge-key.pem

# Connect via SSH
ssh -i bloodbridge-key.pem ec2-user@<public-ip>
```

## 13.4 Deploy Application

```bash
# Update system
sudo yum update -y

# Install Python and pip
sudo yum install python3 python3-pip -y

# Install Git
sudo yum install git -y

# Clone your repository
git clone https://github.com/yourusername/bloodbridge.git
cd bloodbridge

# Install dependencies
pip3 install -r requirements.txt

# Run application
python3 app.py
```

---

# 14. Running Flask on Port 80

## 14.1 Why Port 80?

- Port 80 is the default HTTP port
- Users don't need to specify port in URL
- `http://your-ip` instead of `http://your-ip:5000`

## 14.2 Method 1: Using Gunicorn (Recommended)

```bash
# Install Gunicorn
pip3 install gunicorn

# Run on port 80 (requires sudo)
sudo gunicorn --bind 0.0.0.0:80 app:app --workers 4
```

## 14.3 Method 2: Using iptables (Port Forwarding)

```bash
# Forward port 80 to 5000
sudo iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 5000

# Run Flask on port 5000
python3 app.py
```

## 14.4 Method 3: Using Nginx as Reverse Proxy

```bash
# Install Nginx
sudo yum install nginx -y

# Configure Nginx
sudo nano /etc/nginx/conf.d/bloodbridge.conf
```

```nginx
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Start Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Run Flask
python3 app.py
```

## 14.5 Running as Background Service

```bash
# Create systemd service
sudo nano /etc/systemd/system/bloodbridge.service
```

```ini
[Unit]
Description=BloodBridge Flask Application
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/bloodbridge
ExecStart=/usr/bin/python3 /home/ec2-user/bloodbridge/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable bloodbridge
sudo systemctl start bloodbridge
```

---

# 15. Testing Guide

## 15.1 Functional Testing

| Module | Test | Expected Result |
|--------|------|-----------------|
| Registration | Valid data | Account created |
| Registration | Duplicate email | Error message |
| Registration | Empty fields | Validation error |
| Login | Valid credentials | Dashboard access |
| Login | Invalid password | Error message |
| Request | Create with all fields | Request saved |
| Request | Critical urgency | Appears first in list |
| Donation | Respond to request | Status = accepted |
| Donation | Confirm donation | Status = donated |
| Dashboard | Show compatible requests | Only matching blood types |

## 15.2 Integration Testing

```python
# test_app.py
import unittest
from app import app

class BloodBridgeTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_home_page(self):
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)
    
    def test_login_page(self):
        result = self.app.get('/login')
        self.assertEqual(result.status_code, 200)
    
    def test_register(self):
        result = self.app.post('/register', data={
            'full_name': 'Test User',
            'email': 'test@test.com',
            'password': 'test123',
            'confirm_password': 'test123',
            'blood_group': 'O+'
        })
        self.assertEqual(result.status_code, 302)  # Redirect

if __name__ == '__main__':
    unittest.main()
```

## 15.3 Load Testing

```bash
# Install Apache Bench
sudo yum install httpd-tools -y

# Test with 100 requests, 10 concurrent
ab -n 100 -c 10 http://localhost:5000/
```

---

# 16. Common Errors & Fixes

## 16.1 Flask Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'flask'` | Flask not installed | `pip install flask` |
| `Address already in use` | Port 5000 occupied | Kill process or use different port |
| `TemplateNotFound` | Template missing | Check templates folder |
| `KeyError: 'user_id'` | Session expired | Login again |

## 16.2 DynamoDB Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `ResourceNotFoundException` | Table doesn't exist | Run setup script |
| `ValidationException` | Wrong key type | Check attribute types |
| `AccessDeniedException` | No IAM permissions | Update IAM policy |
| `ProvisionedThroughputExceeded` | Too many requests | Increase capacity |

## 16.3 SNS Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `TopicNotFound` | Topic doesn't exist | Create topic first |
| `AuthorizationError` | No SNS permissions | Update IAM policy |
| `InvalidParameter` | Wrong phone format | Use E.164 format (+1234567890) |

## 16.4 EC2 Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Connection refused` | App not running | Start the application |
| `Permission denied` | Port 80 requires sudo | Use sudo or port forward |
| `Connection timeout` | Security group issue | Open port in security group |

---

# 17. Viva Questions & Answers

## 17.1 Project Overview

**Q1: What is BloodBridge?**
> BloodBridge is a web-based blood bank management system that connects blood donors with recipients. It uses AWS cloud services to provide real-time matching based on blood group compatibility.

**Q2: What problem does it solve?**
> It solves the problem of delayed blood availability during emergencies by:
> - Providing instant donor-recipient matching
> - Sending real-time notifications to compatible donors
> - Tracking blood inventory across locations

**Q3: Why did you choose these technologies?**
> - **Flask**: Lightweight, easy to learn, perfect for small-medium applications
> - **DynamoDB**: Fully managed, scales automatically, low latency
> - **SNS**: Reliable notification delivery, supports multiple protocols
> - **EC2**: Full control over server, easy deployment

## 17.2 Technical Questions

**Q4: Explain blood group compatibility logic.**
> Blood compatibility follows these rules:
> - O- can donate to all (universal donor)
> - AB+ can receive from all (universal recipient)
> - Same blood type can always donate to same type
> - Negative types can donate to positive types (but not reverse)

**Q5: How does Flask session work?**
> Flask session stores user data in a signed cookie:
> 1. On login, we set session variables (user_id, name, blood_group)
> 2. The cookie is sent with every request
> 3. Flask verifies the signature using secret_key
> 4. On logout, session.clear() removes all data

**Q6: What is the difference between SQL and NoSQL?**
> | SQL | NoSQL (DynamoDB) |
> |-----|------------------|
> | Fixed schema | Flexible schema |
> | Tables with rows | Items with attributes |
> | JOINs for relations | Denormalized data |
> | Vertical scaling | Horizontal scaling |

**Q7: What is a Global Secondary Index (GSI)?**
> A GSI allows querying a table using an alternative key:
> - Primary key: user_id (for direct lookups)
> - GSI: email (for login queries)
> - GSI creates a copy of data with different key structure

**Q8: How does SNS ensure message delivery?**
> SNS provides:
> - Message persistence until delivered
> - Retry with exponential backoff
> - Dead-letter queues for failed messages
> - Delivery status logging

## 17.3 AWS Questions

**Q9: Why use DynamoDB instead of RDS?**
> For BloodBridge:
> - Simple key-value access patterns
> - No complex JOINs needed
> - Need to scale quickly during emergencies
> - Pay-per-request pricing for variable load

**Q10: What is an IAM Role?**
> An IAM role is a set of permissions that can be assumed by:
> - AWS services (EC2, Lambda)
> - Users from other accounts
> - Federated users
> Unlike users, roles don't have permanent credentials.

**Q11: How would you scale this application?**
> - **Horizontal scaling**: Add more EC2 instances behind a Load Balancer
> - **Auto Scaling**: Automatically add/remove instances based on load
> - **DynamoDB**: Auto-scales with on-demand mode
> - **CloudFront**: Cache static content at edge locations

---

# 18. Future Enhancements

## 18.1 Feature Enhancements

| Enhancement | Description |
|-------------|-------------|
| **Mobile App** | React Native or Flutter app for donors |
| **GPS Integration** | Find nearest blood banks and donors |
| **AI Matching** | Predict blood demand using ML |
| **Blockchain** | Immutable blood donation records |
| **Video Verification** | Verify donors via video call |

## 18.2 Technical Improvements

| Improvement | Benefit |
|-------------|---------|
| **WebSockets** | Real-time updates without polling |
| **Redis Cache** | Faster data access |
| **Elasticsearch** | Advanced search capabilities |
| **CI/CD Pipeline** | Automated testing and deployment |
| **Microservices** | Better scalability and maintenance |

## 18.3 AWS Service Additions

| Service | Use Case |
|---------|----------|
| **Lambda** | Serverless functions for notifications |
| **API Gateway** | RESTful API for mobile apps |
| **CloudWatch** | Monitoring and alerting |
| **S3** | Store user documents and images |
| **Cognito** | Advanced authentication with MFA |

## 18.4 Sample Enhancement: Lambda for Notifications

```python
# lambda_function.py
import boto3
import json

def lambda_handler(event, context):
    sns = boto3.client('sns')
    
    # Parse event
    blood_group = event['blood_group']
    location = event['location']
    urgency = event['urgency']
    
    # Send notification
    message = f"""
    🩸 BLOOD REQUEST ALERT
    Blood Group: {blood_group}
    Location: {location}
    Urgency: {urgency}
    
    Open BloodBridge app to respond.
    """
    
    sns.publish(
        TopicArn='arn:aws:sns:us-east-1:xxx:bloodbridge-alerts',
        Subject=f'Blood Request: {blood_group}',
        Message=message
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Notification sent!')
    }
```

---

# Conclusion

This guide covers the complete development journey of BloodBridge:

1. ✅ Local development with Flask
2. ✅ User authentication with sessions
3. ✅ Blood request management
4. ✅ AWS DynamoDB integration
5. ✅ SNS notifications
6. ✅ IAM security
7. ✅ EC2 deployment
8. ✅ Production configuration

**Remember:**
- Start local, then move to cloud
- Test thoroughly at each stage
- Follow security best practices
- Document your code
- Prepare for viva with understanding, not memorization

---

*Good luck with your project and viva! 🎓*
