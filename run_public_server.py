#!/usr/bin/env python3
"""
Public API Server for LLM Insurance Claim Evaluation System
Production-ready server with public access
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes_with_webhooks import router

# Create FastAPI app
app = FastAPI(
    title="LLM Insurance Claim Evaluation System",
    description="AI-powered system for evaluating insurance claims using LLM reasoning",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for public access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for public access
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router
app.include_router(router)

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "LLM Insurance Claim Evaluation System is running",
        "version": "1.0.0",
        "status": "public",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "upload": "/upload/",
            "query": "/query/",
            "nl_query": "/nl_query/",
            "files": "/files/",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint"""
    return {
        "status": "healthy",
        "system": "LLM Insurance Claim Evaluator",
        "version": "1.0.0",
        "public": True,
        "endpoints": {
            "upload": "/upload/",
            "query": "/query/",
            "nl_query": "/nl_query/",
            "files": "/files/",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")  # Allow external connections
    
    print("🚀 Starting Public LLM Insurance Claim Evaluation System...")
    print("=" * 80)
    print(f"📋 Server Configuration:")
    print(f"   - Host: {host}")
    print(f"   - Port: {port}")
    print(f"   - Public Access: Enabled")
    print(f"   - API Docs: http://localhost:{port}/docs")
    print(f"   - Health Check: http://localhost:{port}/health")
    print(f"   - CORS: Enabled for all origins")
    print()
    print("🔗 Available Endpoints:")
    print("   - POST /upload/ - Upload insurance documents")
    print("   - POST /query/ - Submit structured queries")
    print("   - POST /nl_query/ - Submit natural language queries")
    print("   - GET /files/ - List uploaded files")
    print("   - DELETE /files/{file_id} - Delete uploaded file")
    print("   - GET /health - Health check")
    print("   - GET /docs - API documentation")
    print()
    print("📖 Example Usage:")
    print("   curl -X POST 'http://localhost:8000/query/' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{")
    print('       "file_id": "your_file_id",')
    print('       "age": 35,')
    print('       "gender": "male",')
    print('       "procedure": "knee surgery",')
    print('       "location": "Mumbai",')
    print('       "policy_duration_months": 12')
    print("     }'")
    print("=" * 80)
    print("🌐 Starting server... (Press Ctrl+C to stop)")
    
    # Start the server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )

