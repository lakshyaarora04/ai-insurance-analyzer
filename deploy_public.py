#!/usr/bin/env python3
"""
Deployment Script for Public API Server
Helps set up the server for public access
"""

import subprocess
import sys
import os
import requests
import time
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "python-multipart",
        "requests",
        "pydantic"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        for package in missing_packages:
            subprocess.run([sys.executable, "-m", "pip", "install", package])
        print("✅ All dependencies installed")
    else:
        print("✅ All dependencies are already installed")

def get_public_ip():
    """Get the public IP address"""
    try:
        response = requests.get("https://api.ipify.org", timeout=5)
        return response.text
    except:
        return "localhost"

def start_server():
    """Start the public server"""
    print("\n🚀 Starting Public API Server...")
    
    # Get configuration
    port = os.getenv("PORT", "8000")
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"📋 Configuration:")
    print(f"   - Host: {host}")
    print(f"   - Port: {port}")
    print(f"   - Public Access: Enabled")
    
    # Start the server
    try:
        subprocess.run([
            sys.executable, "run_public_server.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def test_server():
    """Test if the server is running"""
    print("\n🧪 Testing server...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is running and healthy")
            print(f"   Status: {data.get('status')}")
            print(f"   System: {data.get('system')}")
            print(f"   Version: {data.get('version')}")
            return True
        else:
            print(f"❌ Server responded with status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
        return False
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

def show_access_info():
    """Show information about accessing the server"""
    print("\n🌐 Public Access Information")
    print("=" * 50)
    
    public_ip = get_public_ip()
    
    print(f"📱 Local Access:")
    print(f"   - API: http://localhost:8000")
    print(f"   - Docs: http://localhost:8000/docs")
    print(f"   - Health: http://localhost:8000/health")
    
    print(f"\n🌍 Public Access (if port forwarding is configured):")
    print(f"   - API: http://{public_ip}:8000")
    print(f"   - Docs: http://{public_ip}:8000/docs")
    print(f"   - Health: http://{public_ip}:8000/health")
    
    print(f"\n📋 Environment Variables:")
    print(f"   - PORT: {os.getenv('PORT', '8000')}")
    print(f"   - HOST: {os.getenv('HOST', '0.0.0.0')}")
    
    print(f"\n🔧 To make it publicly accessible:")
    print(f"   1. Configure port forwarding on your router")
    print(f"   2. Forward port 8000 to your local machine")
    print(f"   3. Or use a service like ngrok: ngrok http 8000")

def main():
    """Main deployment function"""
    print("🚀 LLM Insurance Claim Evaluation System - Public Deployment")
    print("=" * 70)
    
    # Check dependencies
    check_dependencies()
    
    # Show access information
    show_access_info()
    
    # Ask user if they want to start the server
    print("\n" + "=" * 70)
    response = input("🤔 Do you want to start the server now? (y/n): ").lower().strip()
    
    if response in ['y', 'yes']:
        start_server()
    else:
        print("💡 To start the server manually, run:")
        print("   python run_public_server.py")
        print("\n💡 Or with custom port:")
        print("   PORT=8080 python run_public_server.py")

if __name__ == "__main__":
    main()

