"""
BloodBridge - Blood Bank Management System
============================================
A Flask application for managing blood donations with real-time features.

Run: python app.py
URL: http://127.0.0.1:5000
Demo: john@demo.com / demo123

Features:
- User registration with phone number
- Blood request management
- Real-time dashboard
- SOS Emergency alerts
- SMS notifications ready (AWS SNS)
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import uuid
import random
import re

# ============================================
# FLASK APP SETUP
# ============================================
# TODO [EC2]: Deploy with gunicorn -w 4 -b 0.0.0.0:5000 app:app

app = Flask(__name__)
app.secret_key = 'bloodbridge-secret-key-change-in-production'

# ============================================
# IN-MEMORY DATABASE (Replace with DynamoDB)
# ============================================

# TODO [DynamoDB]: Replace with DynamoDB table 'bloodbridge_users'
users_db = []

# TODO [DynamoDB]: Replace with DynamoDB table 'bloodbridge_requests'
blood_requests_db = []

# TODO [DynamoDB]: Replace with DynamoDB table 'bloodbridge_emergencies'
emergency_alerts = []

# TODO [DynamoDB]: Replace with DynamoDB table 'bloodbridge_inventory'
blood_inventory = {
    'A+': {'units': 25, 'last_updated': datetime.now().isoformat()},
    'A-': {'units': 12, 'last_updated': datetime.now().isoformat()},
    'B+': {'units': 18, 'last_updated': datetime.now().isoformat()},
    'B-': {'units': 8, 'last_updated': datetime.now().isoformat()},
    'AB+': {'units': 15, 'last_updated': datetime.now().isoformat()},
    'AB-': {'units': 5, 'last_updated': datetime.now().isoformat()},
    'O+': {'units': 30, 'last_updated': datetime.now().isoformat()},
    'O-': {'units': 10, 'last_updated': datetime.now().isoformat()}
}

# Blood camps data
blood_camps = [
    {
        'camp_id': str(uuid.uuid4()),
        'name': 'City Hospital Blood Drive',
        'location': 'City Hospital, Main Street',
        'date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
        'time': '09:00 AM - 05:00 PM',
        'organizer': 'City Hospital',
        'contact': '+1-555-0100',
        'registered': 45,
        'capacity': 100
    },
    {
        'camp_id': str(uuid.uuid4()),
        'name': 'University Blood Donation Camp',
        'location': 'University Auditorium',
        'date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
        'time': '10:00 AM - 04:00 PM',
        'organizer': 'University Health Club',
        'contact': '+1-555-0200',
        'registered': 78,
        'capacity': 150
    }
]
camp_registrations = {}

# Badges system
BADGES = {
    'first_blood': {'name': 'First Blood', 'icon': '🩸', 'description': 'Made your first donation'},
    'lifesaver_3': {'name': 'Lifesaver', 'icon': '💖', 'description': 'Saved 3 lives'},
    'hero': {'name': 'Hero', 'icon': '🦸', 'description': 'Made 5+ donations'},
    'emergency_responder': {'name': 'Emergency Responder', 'icon': '🚨', 'description': 'Responded to emergency'},
    'rare_donor': {'name': 'Rare Donor', 'icon': '💎', 'description': 'Donated rare blood type'}
}
user_badges = {}

# Real-time tracking
online_users = {}
activity_feed = []

# ============================================
# CONSTANTS
# ============================================
BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

# Blood compatibility chart
COMPATIBILITY = {
    'O-': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
    'O+': ['A+', 'B+', 'AB+', 'O+'],
    'A-': ['A+', 'A-', 'AB+', 'AB-'],
    'A+': ['A+', 'AB+'],
    'B-': ['B+', 'B-', 'AB+', 'AB-'],
    'B+': ['B+', 'AB+'],
    'AB-': ['AB+', 'AB-'],
    'AB+': ['AB+']
}

# ============================================
# HELPER FUNCTIONS
# ============================================

def validate_phone(phone):
    """Validate phone number format."""
    # Remove spaces, dashes, parentheses
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    # Check if it's digits only and has valid length (10-15 digits)
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    return cleaned.isdigit() and 10 <= len(cleaned) <= 15


def format_phone(phone):
    """Format phone number for display."""
    cleaned = re.sub(r'[\s\-\(\)\.]', '', phone)
    if not cleaned.startswith('+'):
        # Assume it's a local number, add country code format
        if len(cleaned) == 10:
            return f"+91-{cleaned[:5]}-{cleaned[5:]}"
    return phone


def login_required(f):
    """Decorator to require login for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_user_by_id(user_id):
    """Find user by ID. TODO [DynamoDB]: Replace with get_item()"""
    for user in users_db:
        if user['user_id'] == user_id:
            return user
    return None


def get_user_by_email(email):
    """Find user by email. TODO [DynamoDB]: Replace with query using GSI"""
    for user in users_db:
        if user['email'].lower() == email.lower():
            return user
    return None


def get_user_by_phone(phone):
    """Find user by phone. TODO [DynamoDB]: Replace with query using GSI"""
    cleaned_phone = re.sub(r'[\s\-\(\)\.\+]', '', phone)
    for user in users_db:
        user_phone = re.sub(r'[\s\-\(\)\.\+]', '', user.get('phone', ''))
        if user_phone == cleaned_phone:
            return user
    return None


def get_compatible_requests(user_blood_group):
    """Get blood requests that the user can donate to."""
    compatible_groups = COMPATIBILITY.get(user_blood_group, [])
    matching_requests = []
    
    for req in blood_requests_db:
        if req['blood_group'] in compatible_groups and req['status'] == 'pending':
            requester = get_user_by_id(req['requester_id'])
            req_copy = req.copy()
            req_copy['requester_name'] = requester['full_name'] if requester else 'Unknown'
            req_copy['requester_phone'] = requester.get('phone', 'N/A') if requester else 'N/A'
            matching_requests.append(req_copy)
    
    return matching_requests


def send_notification(recipient, subject, message):
    """
    Send notification.
    TODO [SNS]: Replace with AWS SNS publish
    
    For SMS: Use sns.publish(PhoneNumber=phone, Message=message)
    For Email: Use sns.publish(TopicArn=topic, Message=message)
    """
    print(f"[NOTIFICATION] To: {recipient} | Subject: {subject}")
    print(f"[MESSAGE] {message}")


def send_sms(phone_number, message):
    """
    Send SMS notification.
    TODO [SNS]: Replace with AWS SNS SMS
    
    Example:
        sns.publish(
            PhoneNumber=phone_number,
            Message=message
        )
    """
    print(f"[SMS] To: {phone_number}")
    print(f"[SMS] Message: {message}")


def add_activity(user_id, activity_type, message, icon='🔔'):
    """Add activity to the feed."""
    activity_feed.insert(0, {
        'activity_id': str(uuid.uuid4()),
        'user_id': user_id,
        'type': activity_type,
        'message': message,
        'icon': icon,
        'timestamp': datetime.now().isoformat()
    })
    if len(activity_feed) > 50:
        activity_feed.pop()


def award_badge(user_id, badge_key):
    """Award a badge to user."""
    if user_id not in user_badges:
        user_badges[user_id] = []
    if badge_key not in user_badges[user_id]:
        user_badges[user_id].append(badge_key)
        user = get_user_by_id(user_id)
        if user:
            add_activity(user_id, 'badge', f"{user['full_name']} earned {BADGES[badge_key]['name']}!", BADGES[badge_key]['icon'])
        return True
    return False


def get_user_stats(user_id):
    """Get stats for a user."""
    donations = sum(1 for req in blood_requests_db 
                   if req.get('donor_id') == user_id and req['status'] == 'donated')
    requests = sum(1 for req in blood_requests_db if req['requester_id'] == user_id)
    
    return {
        'donations': donations,
        'requests': requests,
        'lives_saved': donations * 3,
        'badges': user_badges.get(user_id, [])
    }


def update_user_activity(user_id):
    """Update user's last activity timestamp."""
    online_users[user_id] = datetime.now().isoformat()


def get_online_donors_count():
    """Count users active in last 5 minutes."""
    now = datetime.now()
    count = 0
    for user_id, last_active in list(online_users.items()):
        try:
            last_time = datetime.fromisoformat(last_active)
            if (now - last_time).total_seconds() < 300:
                count += 1
        except:
            pass
    return count


def get_realtime_inventory():
    """Get blood inventory with status."""
    inventory = {}
    for blood_type, data in blood_inventory.items():
        units = data['units']
        if units <= 5:
            status = 'critical'
        elif units <= 15:
            status = 'low'
        elif units <= 25:
            status = 'moderate'
        else:
            status = 'sufficient'
        inventory[blood_type] = {'units': units, 'status': status}
    return inventory


def notify_compatible_donors(blood_group, location, urgency, requester_name):
    """
    Notify all compatible donors about a blood request.
    TODO [SNS]: Send SMS to all compatible donors
    """
    # Find donors who can donate to this blood group
    for user in users_db:
        user_blood = user.get('blood_group')
        if blood_group in COMPATIBILITY.get(user_blood, []):
            phone = user.get('phone')
            if phone:
                message = f"🩸 BLOOD REQUEST: {blood_group} needed at {location}. Urgency: {urgency.upper()}. Contact: {requester_name}. Open BloodBridge to respond."
                send_sms(phone, message)


# ============================================
# PUBLIC ROUTES
# ============================================

@app.route('/')
def index():
    """Landing page."""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        blood_group = request.form.get('blood_group', '')
        
        # Validation
        errors = []
        if not full_name:
            errors.append('Full name is required.')
        if not email or '@' not in email:
            errors.append('Valid email is required.')
        if not phone:
            errors.append('Phone number is required.')
        elif not validate_phone(phone):
            errors.append('Please enter a valid phone number (10-15 digits).')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        if blood_group not in BLOOD_GROUPS:
            errors.append('Please select a valid blood group.')
        if get_user_by_email(email):
            errors.append('Email already registered.')
        if phone and get_user_by_phone(phone):
            errors.append('Phone number already registered.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('register.html', blood_groups=BLOOD_GROUPS)
        
        # Create user - TODO [DynamoDB]: Replace with put_item()
        new_user = {
            'user_id': str(uuid.uuid4()),
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'password_hash': generate_password_hash(password),
            'blood_group': blood_group,
            'created_at': datetime.now().isoformat()
        }
        users_db.append(new_user)
        
        add_activity(new_user['user_id'], 'registration', f"🎉 {full_name} joined BloodBridge!", '🎉')
        
        # TODO [SNS]: Send welcome SMS
        send_sms(phone, f"Welcome to BloodBridge, {full_name}! Your account is ready. Start saving lives today!")
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', blood_groups=BLOOD_GROUPS)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        user = get_user_by_email(email)
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['user_id']
            session['user_name'] = user['full_name']
            session['user_email'] = user['email']
            session['user_phone'] = user.get('phone', '')
            session['blood_group'] = user['blood_group']
            
            update_user_activity(user['user_id'])
            flash(f'Welcome back, {user["full_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    """User logout."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ============================================
# DASHBOARD & REQUESTS
# ============================================

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard."""
    update_user_activity(session['user_id'])
    user_blood_group = session.get('blood_group')
    
    matching_requests = get_compatible_requests(user_blood_group)
    urgency_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    matching_requests.sort(key=lambda x: urgency_order.get(x['urgency'], 4))
    
    my_requests = [req for req in blood_requests_db if req['requester_id'] == session['user_id']]
    my_donations = [req for req in blood_requests_db if req.get('donor_id') == session['user_id']]
    
    return render_template('dashboard.html',
        matching_requests=matching_requests,
        my_requests=my_requests,
        my_donations=my_donations,
        user_blood_group=user_blood_group
    )


@app.route('/request/create', methods=['GET', 'POST'])
@login_required
def create_request():
    """Create a new blood request."""
    if request.method == 'POST':
        location = request.form.get('location', '').strip()
        blood_group = request.form.get('blood_group', '')
        quantity = request.form.get('quantity', '')
        urgency = request.form.get('urgency', '')
        contact_phone = request.form.get('contact_phone', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # Validation
        errors = []
        if not location:
            errors.append('Location is required.')
        if blood_group not in BLOOD_GROUPS:
            errors.append('Please select a valid blood group.')
        try:
            quantity = int(quantity)
            if quantity < 1 or quantity > 10:
                errors.append('Quantity must be between 1 and 10.')
        except ValueError:
            errors.append('Quantity must be a number.')
        if urgency not in ['low', 'medium', 'high', 'critical']:
            errors.append('Please select urgency level.')
        if contact_phone and not validate_phone(contact_phone):
            errors.append('Please enter a valid contact phone number.')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('create_request.html', blood_groups=BLOOD_GROUPS)
        
        # Use user's phone if contact phone not provided
        if not contact_phone:
            user = get_user_by_id(session['user_id'])
            contact_phone = user.get('phone', '') if user else ''
        
        # Create request - TODO [DynamoDB]: Replace with put_item()
        new_request = {
            'request_id': str(uuid.uuid4()),
            'requester_id': session['user_id'],
            'blood_group': blood_group,
            'location': location,
            'quantity': quantity,
            'urgency': urgency,
            'contact_phone': contact_phone,
            'notes': notes,
            'status': 'pending',
            'donor_id': None,
            'created_at': datetime.now().isoformat()
        }
        blood_requests_db.append(new_request)
        
        user = get_user_by_id(session['user_id'])
        add_activity(session['user_id'], 'request', 
                    f"{user['full_name']} needs {blood_group} blood at {location}", '🩸')
        
        # TODO [SNS]: Notify compatible donors via SMS
        notify_compatible_donors(blood_group, location, urgency, user['full_name'])
        
        flash('Blood request created successfully! Compatible donors have been notified.', 'success')
        return redirect(url_for('dashboard'))
    
    user = get_user_by_id(session['user_id'])
    return render_template('create_request.html', blood_groups=BLOOD_GROUPS, user=user)


@app.route('/request/<request_id>/respond', methods=['POST'])
@login_required
def respond_to_request(request_id):
    """Respond to a blood request."""
    blood_request = None
    for req in blood_requests_db:
        if req['request_id'] == request_id:
            blood_request = req
            break
    
    if not blood_request:
        flash('Blood request not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    if blood_request['status'] != 'pending':
        flash('This request is no longer available.', 'warning')
        return redirect(url_for('dashboard'))
    
    if blood_request['requester_id'] == session['user_id']:
        flash('You cannot respond to your own request.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Update request
    blood_request['status'] = 'accepted'
    blood_request['donor_id'] = session['user_id']
    blood_request['accepted_at'] = datetime.now().isoformat()
    
    donor = get_user_by_id(session['user_id'])
    requester = get_user_by_id(blood_request['requester_id'])
    
    add_activity(session['user_id'], 'donation_offer', 
                f"{donor['full_name']} offered to donate {blood_request['blood_group']} blood!", '💉')
    
    # TODO [SNS]: Notify requester via SMS
    if requester and requester.get('phone'):
        message = f"Good news! {donor['full_name']} has agreed to donate {blood_request['blood_group']} blood. Contact: {donor.get('phone', 'N/A')}"
        send_sms(requester['phone'], message)
    
    flash('Thank you for offering to donate! The requester has been notified.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/request/<request_id>/confirm', methods=['POST'])
@login_required
def confirm_donation(request_id):
    """Confirm donation completed."""
    blood_request = None
    for req in blood_requests_db:
        if req['request_id'] == request_id:
            blood_request = req
            break
    
    if not blood_request:
        flash('Blood request not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    if blood_request['requester_id'] != session['user_id']:
        flash('Only the requester can confirm.', 'warning')
        return redirect(url_for('dashboard'))
    
    if blood_request['status'] != 'accepted':
        flash('Request must be accepted first.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Update status
    blood_request['status'] = 'donated'
    blood_request['donated_at'] = datetime.now().isoformat()
    
    # Update inventory
    bg = blood_request['blood_group']
    blood_inventory[bg]['units'] += blood_request['quantity']
    blood_inventory[bg]['last_updated'] = datetime.now().isoformat()
    
    # Award badges
    donor_id = blood_request['donor_id']
    donor = get_user_by_id(donor_id)
    
    award_badge(donor_id, 'first_blood')
    
    total_donations = sum(1 for req in blood_requests_db 
                         if req.get('donor_id') == donor_id and req['status'] == 'donated')
    
    if total_donations >= 3:
        award_badge(donor_id, 'lifesaver_3')
    if total_donations >= 5:
        award_badge(donor_id, 'hero')
    
    if donor and donor['blood_group'] in ['AB-', 'B-', 'O-']:
        award_badge(donor_id, 'rare_donor')
    
    add_activity(donor_id, 'donation_complete', 
                f"{donor['full_name']} completed a blood donation! 🎉", '✅')
    
    # TODO [SNS]: Thank donor via SMS
    if donor and donor.get('phone'):
        message = f"Thank you {donor['full_name']}! Your blood donation has been confirmed. You've helped save up to 3 lives! 🩸❤️"
        send_sms(donor['phone'], message)
    
    flash('Donation confirmed! Thank you!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/request/<request_id>/cancel', methods=['POST'])
@login_required
def cancel_request(request_id):
    """Cancel a blood request."""
    blood_request = None
    for req in blood_requests_db:
        if req['request_id'] == request_id:
            blood_request = req
            break
    
    if not blood_request:
        flash('Blood request not found.', 'danger')
        return redirect(url_for('dashboard'))
    
    if blood_request['requester_id'] != session['user_id']:
        flash('Only the requester can cancel.', 'warning')
        return redirect(url_for('dashboard'))
    
    if blood_request['status'] == 'donated':
        flash('Cannot cancel completed donation.', 'warning')
        return redirect(url_for('dashboard'))
    
    blood_request['status'] = 'cancelled'
    flash('Request cancelled.', 'info')
    return redirect(url_for('dashboard'))


@app.route('/all-requests')
@login_required
def all_requests():
    """View all blood requests."""
    all_reqs = []
    for req in blood_requests_db:
        requester = get_user_by_id(req['requester_id'])
        req_copy = req.copy()
        req_copy['requester_name'] = requester['full_name'] if requester else 'Unknown'
        req_copy['requester_phone'] = requester.get('phone', 'N/A') if requester else 'N/A'
        all_reqs.append(req_copy)
    
    all_reqs.sort(key=lambda x: x['created_at'], reverse=True)
    return render_template('all_requests.html', requests=all_reqs)


@app.route('/profile')
@login_required
def profile():
    """User profile page."""
    user = get_user_by_id(session['user_id'])
    stats = get_user_stats(session['user_id'])
    badges = [BADGES[b] for b in stats['badges'] if b in BADGES]
    
    return render_template('profile.html', 
        user=user, 
        stats=stats,
        badges=badges,
        donations_count=stats['donations'], 
        requests_count=stats['requests']
    )


# ============================================
# UNIQUE FEATURES
# ============================================

@app.route('/realtime-dashboard')
@login_required
def realtime_dashboard():
    """Real-time dashboard with live updates."""
    update_user_activity(session['user_id'])
    return render_template('realtime_dashboard.html')


@app.route('/blood-inventory')
@login_required
def blood_inventory_view():
    """View blood inventory."""
    inventory = get_realtime_inventory()
    return render_template('blood_inventory.html', inventory=inventory)


@app.route('/blood-camps')
@login_required
def blood_camps_view():
    """View blood donation camps."""
    user_registrations = camp_registrations.get(session['user_id'], [])
    sorted_camps = sorted(blood_camps, key=lambda x: x['date'])
    return render_template('blood_camps.html', camps=sorted_camps, user_registrations=user_registrations)


@app.route('/blood-camps/<camp_id>/register', methods=['POST'])
@login_required
def register_for_camp(camp_id):
    """Register for a blood camp."""
    camp = None
    for c in blood_camps:
        if c['camp_id'] == camp_id:
            camp = c
            break
    
    if not camp:
        flash('Camp not found.', 'danger')
        return redirect(url_for('blood_camps_view'))
    
    if session['user_id'] not in camp_registrations:
        camp_registrations[session['user_id']] = []
    
    if camp_id in camp_registrations[session['user_id']]:
        flash('Already registered.', 'warning')
        return redirect(url_for('blood_camps_view'))
    
    if camp['registered'] >= camp['capacity']:
        flash('Camp is full.', 'danger')
        return redirect(url_for('blood_camps_view'))
    
    camp_registrations[session['user_id']].append(camp_id)
    camp['registered'] += 1
    
    user = get_user_by_id(session['user_id'])
    add_activity(session['user_id'], 'camp', f"{user['full_name']} registered for {camp['name']}", '🏕️')
    
    # TODO [SNS]: Send confirmation SMS
    if user and user.get('phone'):
        message = f"You're registered for {camp['name']} on {camp['date']}. Location: {camp['location']}. See you there!"
        send_sms(user['phone'], message)
    
    flash(f"Registered for {camp['name']}!", 'success')
    return redirect(url_for('blood_camps_view'))


@app.route('/sos-emergency', methods=['GET', 'POST'])
@login_required
def sos_emergency():
    """One-tap SOS emergency."""
    if request.method == 'POST':
        user = get_user_by_id(session['user_id'])
        
        alert = {
            'alert_id': str(uuid.uuid4()),
            'requester_id': session['user_id'],
            'requester_name': user['full_name'],
            'requester_phone': user.get('phone', ''),
            'blood_group': request.form.get('blood_group', user['blood_group']),
            'location': request.form.get('location', 'Emergency Location'),
            'hospital': request.form.get('hospital', 'Nearest Hospital'),
            'contact_phone': request.form.get('contact_phone', user.get('phone', '')),
            'details': request.form.get('details', 'SOS EMERGENCY - Immediate blood needed!'),
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'responders': []
        }
        emergency_alerts.insert(0, alert)
        
        add_activity(session['user_id'], 'sos', f"🆘 SOS ALERT from {user['full_name']}!", '🆘')
        
        # TODO [SNS]: Broadcast emergency SMS to all compatible donors
        for donor in users_db:
            if donor['user_id'] != session['user_id']:
                donor_blood = donor.get('blood_group')
                if alert['blood_group'] in COMPATIBILITY.get(donor_blood, []):
                    if donor.get('phone'):
                        message = f"🆘 EMERGENCY: {alert['blood_group']} blood needed URGENTLY at {alert['hospital']}! Location: {alert['location']}. Contact: {alert['contact_phone']}. Please help if you can!"
                        send_sms(donor['phone'], message)
        
        flash('🆘 SOS Alert sent! All compatible donors have been notified via SMS!', 'success')
        return redirect(url_for('emergency_list'))
    
    user = get_user_by_id(session['user_id'])
    return render_template('sos_emergency.html', user=user, blood_groups=BLOOD_GROUPS)


@app.route('/emergencies')
@login_required
def emergency_list():
    """View emergency alerts."""
    user_blood_group = session.get('blood_group')
    
    compatible_alerts = []
    for alert in emergency_alerts:
        if alert['status'] == 'active':
            alert_copy = alert.copy()
            can_help = alert['blood_group'] in COMPATIBILITY.get(user_blood_group, [])
            alert_copy['can_help'] = can_help
            alert_copy['responder_count'] = len(alert.get('responders', []))
            compatible_alerts.append(alert_copy)
    
    return render_template('emergency_list.html', alerts=compatible_alerts)


@app.route('/emergency/<alert_id>/respond', methods=['POST'])
@login_required
def respond_to_emergency(alert_id):
    """Respond to emergency."""
    alert = None
    for a in emergency_alerts:
        if a['alert_id'] == alert_id:
            alert = a
            break
    
    if not alert:
        flash('Alert not found.', 'danger')
        return redirect(url_for('emergency_list'))
    
    if session['user_id'] in alert['responders']:
        flash('Already responded.', 'warning')
        return redirect(url_for('emergency_list'))
    
    if alert['requester_id'] == session['user_id']:
        flash('You cannot respond to your own emergency.', 'warning')
        return redirect(url_for('emergency_list'))
    
    alert['responders'].append(session['user_id'])
    award_badge(session['user_id'], 'emergency_responder')
    
    donor = get_user_by_id(session['user_id'])
    add_activity(session['user_id'], 'emergency_response', 
                f"{donor['full_name']} responded to emergency!", '🦸')
    
    # TODO [SNS]: Notify requester about responder via SMS
    if alert.get('contact_phone'):
        message = f"🦸 HELP IS COMING! {donor['full_name']} ({donor['blood_group']}) is responding to your emergency. Contact: {donor.get('phone', 'N/A')}"
        send_sms(alert['contact_phone'], message)
    
    flash('Thank you! The requester has been notified via SMS.', 'success')
    return redirect(url_for('emergency_list'))


@app.route('/leaderboard')
@login_required
def leaderboard():
    """Donor leaderboard."""
    donor_stats = {}
    for req in blood_requests_db:
        if req.get('donor_id') and req['status'] == 'donated':
            donor_id = req['donor_id']
            donor_stats[donor_id] = donor_stats.get(donor_id, 0) + 1
    
    leaderboard_list = []
    for user_id, donations in donor_stats.items():
        user = get_user_by_id(user_id)
        if user:
            leaderboard_list.append({
                'user_id': user_id,
                'name': user['full_name'],
                'blood_group': user['blood_group'],
                'donations': donations,
                'lives_saved': donations * 3,
                'badges': len(user_badges.get(user_id, []))
            })
    
    leaderboard_list.sort(key=lambda x: x['donations'], reverse=True)
    
    for i, entry in enumerate(leaderboard_list):
        entry['rank'] = i + 1
    
    return render_template('leaderboard.html', leaderboard=leaderboard_list[:20])


# ============================================
# API ENDPOINTS (Real-Time Data)
# ============================================

@app.route('/api/realtime-data')
def realtime_data():
    """API for real-time dashboard data."""
    if 'user_id' in session:
        update_user_activity(session['user_id'])
    
    active_requests = sum(1 for req in blood_requests_db if req['status'] == 'pending')
    critical_alerts = sum(1 for alert in emergency_alerts if alert['status'] == 'active')
    donations_today = sum(1 for req in blood_requests_db 
                         if req['status'] == 'donated' and 
                         req.get('donated_at', '')[:10] == datetime.now().strftime('%Y-%m-%d'))
    
    recent_activities = []
    for activity in activity_feed[:10]:
        recent_activities.append({
            'icon': activity.get('icon', '🔔'),
            'message': activity['message'],
            'timestamp': activity['timestamp'],
            'isNew': (datetime.now() - datetime.fromisoformat(activity['timestamp'])).total_seconds() < 60
        })
    
    pending_requests = []
    for req in blood_requests_db:
        if req['status'] == 'pending':
            pending_requests.append({
                'request_id': req['request_id'],
                'blood_group': req['blood_group'],
                'location': req['location'],
                'urgency': req['urgency'],
                'status': req['status']
            })
    
    return jsonify({
        'stats': {
            'active_requests': active_requests,
            'online_donors': get_online_donors_count(),
            'critical_alerts': critical_alerts,
            'donations_today': donations_today
        },
        'inventory': get_realtime_inventory(),
        'activities': recent_activities,
        'requests': pending_requests,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/blood-facts')
def blood_facts():
    """Random blood facts."""
    facts = [
        "One donation can save up to 3 lives!",
        "Blood cannot be manufactured – it can only come from donors.",
        "Type O- is the universal donor blood type.",
        "Only 7% of people have O- blood type.",
        "Red blood cells can be stored for up to 42 days.",
        "A single car accident victim may need up to 100 units of blood.",
        "Blood donation takes only about 10 minutes.",
        "Every 2 seconds, someone needs blood.",
        "AB+ is the universal recipient blood type.",
        "Donated blood is tested for HIV, Hepatitis B & C, and other diseases."
    ]
    return jsonify({'fact': random.choice(facts)})


# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='Page not found', code=404), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error='Server error', code=500), 500


# ============================================
# DEMO DATA
# ============================================

def seed_demo_data():
    """Seed demo data for testing."""
    global users_db, blood_requests_db, activity_feed, emergency_alerts
    
    if users_db:
        return
    
    print("[INFO] Seeding demo data...")
    
    # Demo users with phone numbers
    demo_users = [
        {'name': 'John Smith', 'email': 'john@demo.com', 'phone': '+91-98765-43210', 'blood': 'O+', 'password': 'demo123'},
        {'name': 'Sarah Johnson', 'email': 'sarah@demo.com', 'phone': '+91-98765-43211', 'blood': 'A+', 'password': 'demo123'},
        {'name': 'Mike Wilson', 'email': 'mike@demo.com', 'phone': '+91-98765-43212', 'blood': 'B+', 'password': 'demo123'},
        {'name': 'Emily Davis', 'email': 'emily@demo.com', 'phone': '+91-98765-43213', 'blood': 'AB+', 'password': 'demo123'},
        {'name': 'David Brown', 'email': 'david@demo.com', 'phone': '+91-98765-43214', 'blood': 'O-', 'password': 'demo123'},
        {'name': 'Lisa Garcia', 'email': 'lisa@demo.com', 'phone': '+91-98765-43215', 'blood': 'A-', 'password': 'demo123'},
    ]
    
    for user_data in demo_users:
        users_db.append({
            'user_id': str(uuid.uuid4()),
            'full_name': user_data['name'],
            'email': user_data['email'],
            'phone': user_data['phone'],
            'password_hash': generate_password_hash(user_data['password']),
            'blood_group': user_data['blood'],
            'created_at': datetime.now().isoformat()
        })
    
    # Demo requests with contact phone
    locations = ['City Hospital', 'General Medical Center', 'St. Mary Hospital', 'Apollo Hospital']
    urgencies = ['low', 'medium', 'high', 'critical']
    
    for i in range(6):
        user = users_db[i % len(users_db)]
        blood_requests_db.append({
            'request_id': str(uuid.uuid4()),
            'requester_id': user['user_id'],
            'blood_group': random.choice(BLOOD_GROUPS),
            'location': random.choice(locations),
            'quantity': random.randint(1, 4),
            'urgency': random.choice(urgencies),
            'contact_phone': user['phone'],
            'notes': '',
            'status': 'pending',
            'donor_id': None,
            'created_at': (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat()
        })
    
    # Demo activities
    activities = [
        ('donation_complete', '💉 John Smith donated O+ blood', '✅'),
        ('emergency', '🚨 EMERGENCY: AB- needed at General Medical!', '🚨'),
        ('registration', 'New donor Emily Davis joined!', '🎉'),
        ('request', 'Sarah Johnson needs A+ blood at City Hospital', '🩸'),
    ]
    
    for activity_type, message, icon in activities:
        activity_feed.append({
            'activity_id': str(uuid.uuid4()),
            'user_id': users_db[0]['user_id'],
            'type': activity_type,
            'message': message,
            'icon': icon,
            'timestamp': (datetime.now() - timedelta(minutes=random.randint(1, 120))).isoformat()
        })
    
    # Demo emergency
    emergency_alerts.append({
        'alert_id': str(uuid.uuid4()),
        'requester_id': users_db[0]['user_id'],
        'requester_name': users_db[0]['full_name'],
        'requester_phone': users_db[0]['phone'],
        'blood_group': 'O-',
        'location': 'Downtown Emergency Center',
        'hospital': 'City General Hospital',
        'contact_phone': users_db[0]['phone'],
        'details': 'Accident victim needs immediate transfusion',
        'status': 'active',
        'created_at': datetime.now().isoformat(),
        'responders': []
    })
    
    print("[INFO] Demo data ready!")
    print("[INFO] Login: john@demo.com / demo123")
    print("[INFO] Phone: +91-98765-43210")


# ============================================
# MAIN
# ============================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  BloodBridge - Blood Bank Management System")
    print("  URL: http://127.0.0.1:5000")
    print("  Demo: john@demo.com / demo123")
    print("="*60 + "\n")
    
    seed_demo_data()
    app.run(host='127.0.0.1', port=5000, debug=True)
