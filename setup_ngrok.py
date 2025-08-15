#!/usr/bin/env python3
"""
Ngrok Setup Script for Public API Access
Creates a public URL for the API server
"""

import subprocess
import sys
import os
import requests
import time
import json
from pathlib import Path

def check_ngrok():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(["ngrok", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok is installed")
            return True
        else:
            print("❌ ngrok is not installed")
            return False
    except FileNotFoundError:
        print("❌ ngrok is not installed")
        return False

def install_ngrok():
    """Install ngrok"""
    print("📦 Installing ngrok...")
    
    # For macOS
    if sys.platform == "darwin":
        try:
            subprocess.run(["brew", "install", "ngrok"], check=True)
            print("✅ ngrok installed via Homebrew")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install ngrok via Homebrew")
            print("💡 Please install ngrok manually from https://ngrok.com/download")
            return False
    else:
        print("💡 Please install ngrok manually from https://ngrok.com/download")
        return False

def start_ngrok_tunnel(port=8000):
    """Start ngrok tunnel"""
    print(f"🚀 Starting ngrok tunnel on port {port}...")
    
    try:
        # Start ngrok in background
        process = subprocess.Popen([
            "ngrok", "http", str(port)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment for ngrok to start
        time.sleep(3)
        
        # Get the public URL
        try:
            response = requests.get("http://localhost:4040/api/tunnels", timeout=5)
            if response.status_code == 200:
                tunnels = response.json()["tunnels"]
                if tunnels:
                    public_url = tunnels[0]["public_url"]
                    print(f"✅ Public URL: {public_url}")
                    print(f"📋 API Endpoints:")
                    print(f"   - Health: {public_url}/health")
                    print(f"   - Docs: {public_url}/docs")
                    print(f"   - Upload: {public_url}/upload/")
                    print(f"   - Query: {public_url}/query/")
                    print(f"   - NL Query: {public_url}/nl_query/")
                    
                    return public_url, process
                else:
                    print("❌ No tunnels found")
                    return None, process
            else:
                print("❌ Could not get tunnel information")
                return None, process
        except requests.exceptions.RequestException:
            print("❌ Could not connect to ngrok API")
            return None, process
            
    except Exception as e:
        print(f"❌ Error starting ngrok: {e}")
        return None, None

def test_public_url(url):
    """Test the public URL"""
    print(f"\n🧪 Testing public URL: {url}")
    
    try:
        response = requests.get(f"{url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Public URL is working!")
            print(f"   Status: {data.get('status')}")
            print(f"   System: {data.get('system')}")
            return True
        else:
            print(f"❌ Public URL returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing public URL: {e}")
        return False

def main():
    """Main function"""
    print("🌐 LLM Insurance Claim Evaluation System - Public URL Setup")
    print("=" * 70)
    
    # Check if ngrok is installed
    if not check_ngrok():
        print("\n📦 Installing ngrok...")
        if not install_ngrok():
            print("❌ Please install ngrok manually and try again")
            return
    
    # Check if server is running
    print("\n🔍 Checking if server is running...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running on localhost:8000")
        else:
            print("❌ Server is not responding properly")
            print("💡 Please start the server first: python run_public_server.py")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running")
        print("💡 Please start the server first: python run_public_server.py")
        return
    
    # Start ngrok tunnel
    print("\n🚀 Setting up public URL...")
    public_url, ngrok_process = start_ngrok_tunnel(8000)
    
    if public_url:
        # Test the public URL
        if test_public_url(public_url):
            print("\n🎉 Success! Your API is now publicly accessible!")
            print(f"🌐 Public URL: {public_url}")
            print(f"📚 API Documentation: {public_url}/docs")
            print(f"💚 Health Check: {public_url}/health")
            
            print("\n📋 Example Usage:")
            print(f"curl -X GET '{public_url}/health'")
            print(f"curl -X POST '{public_url}/query/' \\")
            print("  -H 'Content-Type: application/json' \\")
            print("  -d '{")
            print('    "file_id": "your_file_id",')
            print('    "age": 35,')
            print('    "gender": "male",')
            print('    "procedure": "knee surgery",')
            print('    "location": "Mumbai",')
            print('    "policy_duration_months": 12')
            print("  }'")
            
            print("\n⚠️  Important Notes:")
            print("   - This URL is temporary and will change if you restart ngrok")
            print("   - For production, consider using a proper hosting service")
            print("   - Keep the ngrok process running to maintain the public URL")
            
            try:
                print("\n🔄 Press Ctrl+C to stop the tunnel...")
                ngrok_process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping ngrok tunnel...")
                ngrok_process.terminate()
                print("✅ Tunnel stopped")
        else:
            print("❌ Public URL is not working properly")
            if ngrok_process:
                ngrok_process.terminate()
    else:
        print("❌ Failed to create public URL")
        if ngrok_process:
            ngrok_process.terminate()

if __name__ == "__main__":
    main()

