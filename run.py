#!/usr/bin/env python3
"""
BloodBridge - Production Run Script
====================================
This script runs the Flask application in production mode.

Usage:
    Local:      python run.py
    Production: sudo python run.py --port 80
    
Options:
    --port      Port to run on (default: 5000)
    --host      Host to bind to (default: 0.0.0.0)
    --debug     Enable debug mode (default: False)
"""

import os
import sys
import argparse
from app import app, seed_demo_data

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Run BloodBridge Application')
    parser.add_argument('--port', type=int, default=5000, help='Port to run on (default: 5000)')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    return parser.parse_args()

def print_banner(host, port):
    """Print startup banner."""
    print("\n" + "="*60)
    print("  🩸 BloodBridge - Blood Bank Management System")
    print("="*60)
    print(f"  Status:  RUNNING")
    print(f"  URL:     http://{host}:{port}")
    if host == '0.0.0.0':
        import socket
        local_ip = socket.gethostbyname(socket.gethostname())
        print(f"  Network: http://{local_ip}:{port}")
    print(f"  Demo:    john@demo.com / demo123")
    print("="*60)
    print("  Press Ctrl+C to stop the server")
    print("="*60 + "\n")

def main():
    """Main entry point."""
    args = parse_args()
    
    # Set environment
    if args.debug:
        os.environ['FLASK_ENV'] = 'development'
    else:
        os.environ['FLASK_ENV'] = 'production'
    
    # Seed demo data
    seed_demo_data()
    
    # Print banner
    print_banner(args.host, args.port)
    
    # Run app
    try:
        if args.debug:
            app.run(host=args.host, port=args.port, debug=True)
        else:
            # Production mode - disable debug
            app.run(host=args.host, port=args.port, debug=False, threaded=True)
    except PermissionError:
        if args.port < 1024:
            print(f"\n❌ Error: Port {args.port} requires root/admin privileges.")
            print(f"   Run with: sudo python run.py --port {args.port}")
            print(f"   Or use a port > 1024: python run.py --port 5000\n")
            sys.exit(1)
        raise
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Error: Port {args.port} is already in use.")
            print(f"   Kill the process: kill $(lsof -t -i:{args.port})")
            print(f"   Or use a different port: python run.py --port 5001\n")
            sys.exit(1)
        raise

if __name__ == '__main__':
    main()