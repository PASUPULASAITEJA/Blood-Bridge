import os
import uuid
import random
import re
import logging
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request,
    redirect, url_for, session,
    flash, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash

# =========================================================
# FLASK APP SETUP
# =========================================================
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(32).hex())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================================================
# AWS / LOCAL MODE
# =========================================================
USE_AWS = os.getenv("USE_AWS", "false").lower() == "true"

if USE_AWS:
    try:
        import aws.dynamodb_helper as dynamodb_helper
        from aws.dynamodb_helper import (
            create_user,
            create_blood_request,
            get_blood_request,
            get_all_pending_requests,
            get_user_blood_requests,
            update_blood_request,
            update_inventory,
            get_inventory,
            create_emergency_alert,
            get_emergency_alerts,
            update_emergency_alert,
        )
        from aws.sns_helper import send_sms, send_emergency_alert
        logger.info("✅ AWS MODE ENABLED")
    except Exception as e:
        logger.error(f"AWS init failed: {e}")
        USE_AWS = False

if not USE_AWS:
    logger.info("⚠️ LOCAL MODE ENABLED")

# =========================================================
# LOCAL STORAGE
# =========================================================
users_db = []
blood_requests_db = []
emergency_alerts = []
activity_feed = []
online_users = {}
user_badges = {}
camp_registrations = {}

blood_inventory = {
    bg: {"units": 20, "last_updated": datetime.now().isoformat()}
    for bg in ['A+','A-','B+','B-','AB+','AB-','O+','O-']
}

# =========================================================
# CONSTANTS
# =========================================================
BLOOD_GROUPS = ['A+','A-','B+','B-','AB+','AB-','O+','O-']

COMPATIBILITY = {
    'O-': BLOOD_GROUPS,
    'O+': ['A+','B+','AB+','O+'],
    'A-': ['A+','A-','AB+','AB-'],
    'A+': ['A+','AB+'],
    'B-': ['B+','B-','AB+','AB-'],
    'B+': ['B+','AB+'],
    'AB-': ['AB+','AB-'],
    'AB+': ['AB+']
}

BADGES = {
    'first_blood': {'name': 'First Blood', 'icon': '🩸'},
    'lifesaver_3': {'name': 'Lifesaver', 'icon': '💖'},
    'hero': {'name': 'Hero', 'icon': '🦸'},
    'emergency_responder': {'name': 'Emergency Responder', 'icon': '🚨'},
    'rare_donor': {'name': 'Rare Donor', 'icon': '💎'}
}

# =========================================================
# HELPERS
# =========================================================
def validate_phone(phone):
    phone = re.sub(r'\D', '', phone)
    return phone.isdigit() and 10 <= len(phone) <= 15


def login_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*a, **kw)
    return wrapper


def get_local_user_by_id(uid):
    return next((u for u in users_db if u['user_id'] == uid), None)


def get_local_user_by_email(email):
    return next((u for u in users_db if u['email'] == email), None)


def get_local_user_by_phone(phone):
    phone = re.sub(r'\D', '', phone)
    return next((u for u in users_db if re.sub(r'\D', '', u.get('phone','')) == phone), None)


# ===== FIXED (NO RECURSION) =====
def get_user_by_id(uid):
    if USE_AWS:
        try:
            return dynamodb_helper.get_user_by_id(uid)
        except:
            return get_local_user_by_id(uid)
    return get_local_user_by_id(uid)


def get_user_by_email(email):
    if USE_AWS:
        try:
            return dynamodb_helper.get_user_by_email(email)
        except:
            return get_local_user_by_email(email)
    return get_local_user_by_email(email)


def get_user_by_phone(phone):
    if USE_AWS:
        try:
            return dynamodb_helper.get_user_by_phone(phone)
        except:
            return get_local_user_by_phone(phone)
    return get_local_user_by_phone(phone)


def add_activity(uid, msg, icon="🔔"):
    activity_feed.insert(0, {
        "id": str(uuid.uuid4()),
        "msg": msg,
        "icon": icon,
        "time": datetime.now().isoformat()
    })
    activity_feed[:] = activity_feed[:50]


def send_notification_sms(phone, msg):
    if USE_AWS:
        try:
            send_sms(phone, msg)
        except:
            pass
    else:
        logger.info(f"[SMS] {phone} → {msg}")


# =========================================================
# ROUTES
# =========================================================
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'].lower()
        if get_user_by_email(email):
            flash("Email already exists")
            return redirect(url_for('register'))

        user = {
            "user_id": str(uuid.uuid4()),
            "full_name": request.form['full_name'],
            "email": email,
            "phone": request.form['phone'],
            "password_hash": generate_password_hash(request.form['password']),
            "blood_group": request.form['blood_group'],
            "created_at": datetime.now().isoformat()
        }

        if USE_AWS:
            create_user(user)
        else:
            users_db.append(user)

        flash("Registration successful")
        return redirect(url_for('login'))

    return render_template("register.html", blood_groups=BLOOD_GROUPS)


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user = get_user_by_email(request.form['email'].lower())
        if user and check_password_hash(user['password_hash'], request.form['password']):
            session['user_id'] = user['user_id']
            session['blood_group'] = user['blood_group']
            return redirect(url_for('dashboard'))
        flash("Invalid credentials")
    return render_template("login.html")


@app.route('/dashboard')
@login_required
def dashboard():
    uid = session['user_id']
    if USE_AWS:
        my_requests = get_user_blood_requests(uid)
    else:
        my_requests = [r for r in blood_requests_db if r['requester_id'] == uid]

    return render_template("dashboard.html", my_requests=my_requests)


@app.route('/request/create', methods=['GET','POST'])
@login_required
def create_request():
    if request.method == 'POST':
        req = {
            "request_id": str(uuid.uuid4()),
            "requester_id": session['user_id'],
            "blood_group": request.form['blood_group'],
            "location": request.form['location'],
            "quantity": int(request.form['quantity']),
            "urgency": request.form['urgency'],
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }

        if USE_AWS:
            create_blood_request(req)
        else:
            blood_requests_db.append(req)

        user = get_user_by_id(session['user_id'])
        add_activity(user['user_id'], f"{user['full_name']} requested blood", "🩸")

        return redirect(url_for('dashboard'))

    return render_template("create_request.html", blood_groups=BLOOD_GROUPS)


@app.route('/leaderboard')
@login_required
def leaderboard():
    stats = {}
    source = get_all_pending_requests() if USE_AWS else blood_requests_db

    for r in source:
        if r.get('donor_id') and r['status'] == 'donated':
            stats[r['donor_id']] = stats.get(r['donor_id'], 0) + 1

    board = []
    for uid, d in stats.items():
        u = get_user_by_id(uid)
        if u:
            board.append({"name": u['full_name'], "donations": d})

    board.sort(key=lambda x: x['donations'], reverse=True)
    return render_template("leaderboard.html", leaderboard=board)


# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":
    if not USE_AWS and not users_db:
        users_db.append({
            "user_id": str(uuid.uuid4()),
            "full_name": "John Demo",
            "email": "john@demo.com",
            "phone": "9999999999",
            "password_hash": generate_password_hash("demo123"),
            "blood_group": "O+",
            "created_at": datetime.now().isoformat()
        })

    app.run(host="0.0.0.0", port=5000, debug=True)
