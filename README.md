# 🩸 BloodBridge - Blood Bank Management System

**Optimizing Lifesaving Resources Using AWS Services**

A Flask-based web application for managing blood donations with real-time features and SMS notifications.

---

## 📋 Features

### Core Features
- ✅ User Registration with **Phone Number**
- ✅ Secure Login/Logout with Flask Sessions
- ✅ Dashboard with Compatible Blood Requests
- ✅ Create & Manage Blood Requests
- ✅ Donor Response & Confirmation System
- ✅ Blood Group Compatibility Matching

### Unique Features
- ⚡ **Real-Time Dashboard** - Live stats, inventory, activity feed
- 🆘 **SOS Emergency Mode** - One-tap emergency with SMS broadcast
- 📱 **SMS Notifications** - Alert donors via phone (AWS SNS ready)
- 📊 **Blood Inventory** - Live stock levels
- 🏕️ **Blood Camps** - Event registration
- 🏆 **Leaderboard** - Gamified donor rankings
- 📞 **Click-to-Call** - Direct phone contact for emergencies

---

## 🛠 Technology Stack

| Component | Technology |
|-----------|------------|
| Backend | Python Flask |
| Frontend | HTML, CSS (Tailwind), Jinja2 |
| Database | Python lists/dicts (local) → DynamoDB (AWS) |
| SMS | Console logs (local) → AWS SNS (cloud) |
| Auth | Flask Sessions |

---

## 📁 Project Structure

```
bloodbridge/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── requirements.txt          # Dependencies
├── README.md                 # This file
├── DEVELOPMENT_GUIDE.md      # Academic development guide
│
├── templates/
│   ├── base.html             # Base template
│   ├── index.html            # Landing page
│   ├── login.html            # Login
│   ├── register.html         # Registration (with phone)
│   ├── dashboard.html        # User dashboard
│   ├── create_request.html   # Create request (with phone)
│   ├── all_requests.html     # All requests
│   ├── profile.html          # Profile (shows phone)
│   ├── realtime_dashboard.html # Real-time dashboard
│   ├── blood_inventory.html  # Inventory
│   ├── blood_camps.html      # Camps
│   ├── sos_emergency.html    # SOS (with phone)
│   ├── emergency_list.html   # Emergencies (call button)
│   ├── leaderboard.html      # Rankings
│   └── error.html            # Errors
│
└── aws/
    ├── dynamodb_setup.py     # DynamoDB tables
    ├── dynamodb_helper.py    # DynamoDB CRUD
    ├── sns_setup.py          # SNS topics
    ├── sns_helper.py         # SMS functions
    └── iam_policy.json       # IAM policy
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install flask werkzeug
```

### 2. Run Application
```bash
python app.py
```

### 3. Open Browser
```
http://127.0.0.1:5000
```

### 4. Demo Login
| Field | Value |
|-------|-------|
| Email | john@demo.com |
| Password | demo123 |
| Phone | +91-98765-43210 |

---

## 📱 Phone Number Features

### Registration
- Phone number required during signup
- Validates 10-15 digit formats
- Stored for SMS notifications

### Blood Requests
- Contact phone included with each request
- Donors can see requester's phone
- Click-to-call button for quick contact

### SOS Emergency
- Phone number prominently displayed
- All compatible donors receive SMS with contact
- Direct call button in emergency list

### SMS Notifications (When AWS Connected)
```
📱 Scenarios that trigger SMS:
1. New user registration → Welcome SMS
2. Blood request created → Notify compatible donors
3. Donor responds → Notify requester
4. Donation confirmed → Thank you SMS
5. SOS Emergency → Broadcast to all compatible donors
```

---

## 🩸 Blood Compatibility

| Type | Can Donate To | Can Receive From |
|------|---------------|------------------|
| O-   | All ✅ | O- only |
| O+   | O+, A+, B+, AB+ | O-, O+ |
| A-   | A+, A-, AB+, AB- | O-, A- |
| A+   | A+, AB+ | O-, O+, A-, A+ |
| B-   | B+, B-, AB+, AB- | O-, B- |
| B+   | B+, AB+ | O-, O+, B-, B+ |
| AB-  | AB+, AB- | O-, A-, B-, AB- |
| AB+  | AB+ only | All ✅ |

---

## ☁️ AWS Integration (Future)

### Local → AWS Migration

| Local (Current) | AWS (Future) |
|-----------------|--------------|
| Python lists | DynamoDB tables |
| print() logs | AWS SNS SMS |
| localhost | EC2 instance |
| Flask sessions | Cognito (optional) |

### Deploy to AWS
```bash
# 1. Install boto3
pip install boto3

# 2. Configure AWS CLI
aws configure

# 3. Create DynamoDB tables
python aws/dynamodb_setup.py

# 4. Create SNS topics
python aws/sns_setup.py

# 5. Deploy to EC2
# See DEVELOPMENT_GUIDE.md
```

---

## 📞 SMS Examples (Console Output)

When running locally, SMS are printed to console:

```
==================================================
📱 SMS NOTIFICATION
==================================================
To: +919876543210
Message: 🩸 A+ blood needed at City Hospital. Contact: +919876543211. Open BloodBridge to respond.
==================================================
```

```
==================================================
📱 SMS NOTIFICATION
==================================================
To: +919876543210
Message: 🆘 EMERGENCY: O- blood needed URGENTLY at General Hospital! Contact John: +919876543211. Please help!
==================================================
```

---

## 🧪 Testing

### Test Flow
1. Register User A (O+ blood, with phone)
2. Register User B (A+ blood, with phone)
3. Login as User B → Create blood request for A+
4. Check console → SMS sent to User A (compatible donor)
5. Login as User A → See request on dashboard
6. Click "Call" to contact User B directly
7. Click "Donate" to respond
8. Check console → SMS sent to User B (donor found!)
9. Login as User B → Confirm donation
10. Check console → Thank you SMS sent to User A


## 📝 License

Academic project for final year evaluation.

---

**Made with ❤️ for saving lives**

*BloodBridge - Every Drop Counts*
