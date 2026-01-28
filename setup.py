#!/usr/bin/env python3
"""
BloodBridge - Setup Script
===========================
This script helps set up the BloodBridge project for first-time users.

Usage:
    python setup.py
"""

import os
import sys
import subprocess

def print_header():
    """Print setup header."""
    print("\n" + "="*60)
    print("  🩸 BloodBridge - Project Setup")
    print("="*60 + "\n")

def check_python():
    """Check Python version."""
    print("1️⃣  Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} - OK\n")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor} - Need 3.8+\n")
        print("   Download from: https://python.org\n")
        return False

def check_pip():
    """Check if pip is available."""
    print("2️⃣  Checking pip...")
    try:
        import pip
        print(f"   ✅ pip available - OK\n")
        return True
    except ImportError:
        print("   ❌ pip not found\n")
        return False

def install_dependencies():
    """Install required packages."""
    print("3️⃣  Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask', 'werkzeug', '-q'])
        print("   ✅ Flask installed\n")
        print("   ✅ Werkzeug installed\n")
        return True
    except subprocess.CalledProcessError:
        print("   ❌ Failed to install dependencies\n")
        return False

def check_templates():
    """Check if templates exist."""
    print("4️⃣  Checking templates folder...")
    templates = [
        'base.html', 'index.html', 'login.html', 'register.html',
        'dashboard.html', 'create_request.html', 'all_requests.html',
        'profile.html', 'realtime_dashboard.html', 'blood_inventory.html',
        'blood_camps.html', 'sos_emergency.html', 'emergency_list.html',
        'leaderboard.html', 'error.html'
    ]
    
    missing = []
    for template in templates:
        path = os.path.join('templates', template)
        if not os.path.exists(path):
            missing.append(template)
    
    if missing:
        print(f"   ❌ Missing templates: {', '.join(missing)}\n")
        return False
    else:
        print(f"   ✅ All {len(templates)} templates found\n")
        return True

def check_app():
    """Check if app.py exists."""
    print("5️⃣  Checking app.py...")
    if os.path.exists('app.py'):
        print("   ✅ app.py found\n")
        return True
    else:
        print("   ❌ app.py not found\n")
        return False

def print_success():
    """Print success message."""
    print("="*60)
    print("  ✅ Setup Complete!")
    print("="*60)
    print("""
  To run the application:
  
    python app.py
    
  Then open in browser:
  
    http://127.0.0.1:5000
    
  Demo login:
  
    Email:    john@demo.com
    Password: demo123
    Phone:    +91-98765-43210
    
""")
    print("="*60 + "\n")

def print_failure():
    """Print failure message."""
    print("="*60)
    print("  ❌ Setup Failed!")
    print("="*60)
    print("""
  Please fix the errors above and run setup again.
  
  For help, see:
    - README.md
    - DEPLOYMENT_GUIDE.md
    
""")
    print("="*60 + "\n")

def main():
    """Main setup function."""
    print_header()
    
    checks = [
        check_python(),
        check_pip(),
        install_dependencies(),
        check_app(),
        check_templates()
    ]
    
    if all(checks):
        print_success()
        return 0
    else:
        print_failure()
        return 1

if __name__ == '__main__':
    sys.exit(main())
