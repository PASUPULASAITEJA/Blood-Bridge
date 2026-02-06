import os
import uuid
import random
import re
import logging
from datetime import datetime, timedelta
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash

# ================== APP SETUP ==================

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(32).hex())

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== AWS SETUP ==================

USE_AWS = os.getenv("USE_AWS", "false").lower() == "true"

if USE_AWS:
    try:
        import aws.dynamodb_helper as dynamodb_helper
        from aws.sns_helper import send_sms, send_emergency_alert
        logger.info("✅ AWS MODE ENABLED")
    except Exception as e:
        logger.error(f"AWS init failed: {e}")
        USE_AWS = False

# ================== LOCAL STORAGE ==================

users_db = []
blood_requests_db = []
emergency_alerts = []
blood_inventory = {
    'A+': {'units': 25}, 'A-': {'units': 12},
    'B+': {'units': 18}, 'B-': {'units': 8},
    'AB+': {'units': 15}, 'AB-': {'units': 5},
    'O+': {'units': 30}, 'O-': {'units': 10}
}

# ================== CONSTANTS ==================

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

# ================== HELPERS ==================

def validate_phone(phone):
    cleaned = re.sub(r"[^\d]", "", phone)
    return cleaned.isdigit() and 10 <= len(cleaned) <= 15


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


# ---------- USER HELPERS (FIXED – NO RECURSION) ----------

def get_local_user_by_id(uid):
    return next((u for u in users_db if u["user_id"] == uid), None)


def get_local_user_by_email(email):
    return next((u for u in users_db if u["email"] == email), None)


def get_user_by_id(uid):
    if USE_AWS:
        try:
            return dynamodb_helper.get_user_by_id(uid)
        except Exception as e:
            logger.error(e)
    return get_local_user_by_id(uid)


def get_user_by_email(email):
    if USE_AWS:
        try:
            return dynamodb_helper.get_user_by_email(email)
        except Exception as e:
            logger.error(e)
    return get_local_user_by_email(email)


# ================== ROUTES ==================

@app.route("/")
def index():
    return render_template("index.html")


# ---------- REGISTER ----------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].lower()
        password = request.form["password"]

        if get_user_by_email(email):
            flash("Email already exists", "danger")
            return redirect(url_for("register"))

        user = {
            "user_id": str(uuid.uuid4()),
            "full_name": request.form["full_name"],
            "email": email,
            "phone": request.form["phone"],
            "blood_group": request.form["blood_group"],
            "password_hash": generate_password_hash(password),
            "created_at": datetime.utcnow().isoformat()
        }

        if USE_AWS:
            dynamodb_helper.create_user(user)
        else:
            users_db.append(user)

        flash("Registration successful", "success")
        return redirect(url_for("login"))

    return render_template("register.html", blood_groups=BLOOD_GROUPS)


# ---------- LOGIN ----------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = get_user_by_email(request.form["email"].lower())

        if user and check_password_hash(user["password_hash"], request.form["password"]):
            session["user_id"] = user["user_id"]
            session["blood_group"] = user["blood_group"]
            flash("Login successful", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid credentials", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ---------- DASHBOARD ----------

@app.route("/dashboard")
@login_required
def dashboard():
    user = get_user_by_id(session["user_id"])
    if not user:
        return redirect(url_for("login"))

    if USE_AWS:
        requests = dynamodb_helper.get_all_pending_requests()
    else:
        requests = blood_requests_db

    return render_template(
        "dashboard.html",
        requests=requests,
        blood_group=user["blood_group"]
    )


# ---------- CREATE REQUEST (FIXED) ----------

@app.route("/request/create", methods=["GET", "POST"])
@login_required
def create_request():
    if request.method == "POST":
        user = get_user_by_id(session["user_id"])
        if not user:
            return redirect(url_for("login"))

        req = {
            "request_id": str(uuid.uuid4()),
            "requester_id": user["user_id"],
            "blood_group": request.form["blood_group"],
            "location": request.form["location"],
            "quantity": int(request.form["quantity"]),
            "urgency": request.form["urgency"],
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }

        if USE_AWS:
            dynamodb_helper.create_request(req)
        else:
            blood_requests_db.append(req)

        flash("Blood request created successfully", "success")
        return redirect(url_for("dashboard"))

    return render_template("create_request.html", blood_groups=BLOOD_GROUPS)


# ================== API ==================

@app.route("/api/blood-facts")
def blood_facts():
    facts = [
        "One donation can save 3 lives",
        "O- is universal donor",
        "Blood cannot be manufactured"
    ]
    return jsonify({"fact": random.choice(facts)})


# ================== ERRORS ==================

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500), 500


# ================== MAIN ==================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
