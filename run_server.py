#!/usr/bin/env python3
"""
FastAPI Server Runner for LLM Insurance Claim Evaluation System
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("🚀 Starting LLM Insurance Claim Evaluation System...")
    print("=" * 60)
    
    # Check if OpenAI API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  WARNING: OPENAI_API_KEY not found in environment variables")
        print("   Please set your OpenAI API key:")
        print("   export OPENAI_API_KEY=your_api_key_here")
        print("   Or create a .env file with: OPENAI_API_KEY=your_api_key_here")
        print()
    
    print("📋 Server Configuration:")
    print(f"   - Host: 0.0.0.0")
    print(f"   - Port: 8000")
    print(f"   - API Docs: http://localhost:8000/docs")
    print(f"   - Health Check: http://localhost:8000/health")
    print()
    
    print("🔗 Available Endpoints:")
    print("   - POST /query/ - Submit insurance claim for evaluation")
    print("   - GET / - System status")
    print("   - GET /health - Health check")
    print()
    
    print("📖 Example Query:")
    print("""
    {
        "age": 40,
        "gender": "male",
        "procedure": "cataract surgery",
        "location": "Pune",
        "policy_duration_months": 24
    }
    """)
    
    print("=" * 60)
    print("🌐 Starting server... (Press Ctrl+C to stop)")
    print()
    
    # Run the server
    uvicorn.run(
        "backend.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main() 