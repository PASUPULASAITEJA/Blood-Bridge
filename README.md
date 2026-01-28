# 🩸 BloodBridge - Blood Bank Management System

**Optimizing Lifesaving Resources Using AWS Services**

A Flask-based web application for managing blood donations with real-time features and SMS notifications.

---

## 🚀 Quick Start (Local Deployment)

### Step 1: Install Python
Download from https://python.org (version 3.8+)

### Step 2: Open Terminal
```bash
cd path/to/bloodbridge
```

### Step 3: Run Setup
```bash
python setup.py
```

### Step 4: Start Application
```bash
python app.py
```

### Step 5: Open Browser
```
http://127.0.0.1:5000
```

### Step 6: Login
| Field | Value |
|-------|-------|
| Email | john@demo.com |
| Password | demo123 |
| Phone | +91-98765-43210 |

---

## 📁 Project Structure

```
bloodbridge/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── requirements.txt          # Dependencies
├── setup.py                  # Setup script
├── run.py                    # Production run script
├── README.md                 # This file
├── DEPLOYMENT_GUIDE.md       # Full deployment guide
├── DEVELOPMENT_GUIDE.md      # Academic development guide
│
├── templates/                # HTML Templates
│   ├── base.html             # Base template
│   ├── index.html            # Landing page
│   ├── login.html            # Login
│   ├── register.html         # Registration
│   ├── dashboard.html        # Dashboard
│   ├── create_request.html   # Create request
│   ├── all_requests.html     # All requests
│   ├── profile.html          # Profile
│   ├── realtime_dashboard.html # Real-time dashboard
│   ├── blood_inventory.html  # Inventory
│   ├── blood_camps.html      # Camps
│   ├── sos_emergency.html    # SOS
│   ├── emergency_list.html   # Emergencies
│   ├── leaderboard.html      # Leaderboard
│   └── error.html            # Errors
│
└── aws/                      # AWS Integration
    ├── dynamodb_setup.py     # DynamoDB tables
    ├── dynamodb_helper.py    # DynamoDB CRUD
    ├── sns_setup.py          # SNS topics
    ├── sns_helper.py         # SMS functions
    └── iam_policy.json       # IAM policy
```

---

## ✨ Features

### Core Features
- ✅ User Registration with Phone Number
- ✅ Secure Login/Logout
- ✅ Password Hashing
- ✅ Blood Group Compatibility Matching
- ✅ Create Blood Requests
- ✅ Respond to Requests
- ✅ Confirm Donations

### Unique Features
- ⚡ **Real-Time Dashboard** - Live stats, inventory, activity feed
- 🆘 **SOS Emergency** - One-tap emergency with SMS broadcast
- 📱 **SMS Notifications** - Alert donors via phone
- 📊 **Blood Inventory** - Live stock levels
- 🏕️ **Blood Camps** - Event registration
- 🏆 **Leaderboard** - Gamified donor rankings
- 📞 **Click-to-Call** - Direct phone contact

---

## 📱 SMS Notification Points

| Event | SMS Sent To |
|-------|-------------|
| New Request | All compatible donors |
| Donor Responds | Requester |
| Donation Confirmed | Donor (thank you) |
| SOS Emergency | ALL compatible donors |
| Camp Registration | Registered user |

---

## 🩸 Blood Compatibility

| Donor | Can Donate To |
|-------|---------------|
| O- | All (Universal) |
| O+ | O+, A+, B+, AB+ |
| A- | A-, A+, AB-, AB+ |
| A+ | A+, AB+ |
| B- | B-, B+, AB-, AB+ |
| B+ | B+, AB+ |
| AB- | AB-, AB+ |
| AB+ | AB+ only |

---

## 🧪 Testing

### Test Flow
1. Register User A (O+ blood)
2. Register User B (A+ blood)
3. Login as User B → Create A+ request
4. See SMS in terminal
5. Login as User A → See request → Click Donate
6. Login as User B → Click Confirm
7. Check Profile → See stats

### Demo Users
| Name | Email | Password | Phone | Blood |
|------|-------|----------|-------|-------|
| John Smith | john@demo.com | demo123 | +91-98765-43210 | O+ |
| Sarah Johnson | sarah@demo.com | demo123 | +91-98765-43211 | A+ |
| Mike Wilson | mike@demo.com | demo123 | +91-98765-43212 | B+ |

---

## ☁️ AWS Deployment

See `DEPLOYMENT_GUIDE.md` for full instructions.

### Quick Steps:
```bash
# 1. Install boto3
pip install boto3

# 2. Configure AWS
aws configure

# 3. Create DynamoDB tables
python aws/dynamodb_setup.py

# 4. Create SNS topics
python aws/sns_setup.py

# 5. Deploy to EC2
# See DEPLOYMENT_GUIDE.md
```

---

## 📚 Documentation

| File | Description |
|------|-------------|
| README.md | Quick start guide |
| DEPLOYMENT_GUIDE.md | Full deployment steps |
| DEVELOPMENT_GUIDE.md | Academic guide with viva Q&A |

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| `python not found` | Use `python3` |
| `pip not found` | Use `pip3` |
| `ModuleNotFoundError: flask` | Run `pip install flask` |
| `Address already in use` | Kill process on port 5000 |
| `TemplateNotFound` | Check templates folder |

---

## 👨‍💻 For Viva

Key points to explain:
1. **Flask Sessions** - How user authentication works
2. **Password Hashing** - Why we hash passwords
3. **Blood Compatibility** - O- universal donor logic
4. **DynamoDB** - NoSQL vs SQL differences
5. **SNS** - How SMS notifications work
6. **EC2** - Cloud deployment process

See `DEVELOPMENT_GUIDE.md` for 20+ viva Q&A.

---

## 📝 License

Academic project for final year evaluation.

---

**Made with ❤️ for saving lives**

*BloodBridge - Every Drop Counts*
