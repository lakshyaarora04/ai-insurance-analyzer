# Public API Deployment Guide

## 🚀 Overview

This guide will help you make your LLM Insurance Claim Evaluation System API publicly accessible. The system is designed to work with only the backend, making it perfect for public deployment.

## 📋 Prerequisites

- Python 3.8+
- Required packages: `fastapi`, `uvicorn`, `python-multipart`, `requests`, `pydantic`
- Internet connection for public access

## 🔧 Quick Setup

### 1. Install Dependencies
```bash
pip install fastapi uvicorn python-multipart requests pydantic
```

### 2. Start the Public Server
```bash
python run_public_server.py
```

The server will start on `http://0.0.0.0:8000` and be accessible from any network interface.

## 🌐 Making it Publicly Accessible

### Option 1: Using ngrok (Recommended for Testing)

1. **Install ngrok:**
   ```bash
   # On macOS
   brew install ngrok
   
   # Or download from https://ngrok.com/download
   ```

2. **Start the server:**
   ```bash
   python run_public_server.py
   ```

3. **Create public tunnel:**
   ```bash
   ngrok http 8000
   ```

4. **Use the provided public URL** (e.g., `https://abc123.ngrok.io`)

### Option 2: Using the Setup Script

```bash
python setup_ngrok.py
```

This script will:
- Check if ngrok is installed
- Install ngrok if needed
- Start the server
- Create a public tunnel
- Test the public URL

### Option 3: Manual Port Forwarding

1. **Configure your router** to forward port 8000 to your local machine
2. **Find your public IP** using `curl ifconfig.me`
3. **Access via** `http://YOUR_PUBLIC_IP:8000`

### Option 4: Cloud Deployment

#### Heroku
```bash
# Create Procfile
echo "web: uvicorn run_public_server:app --host=0.0.0.0 --port=\$PORT" > Procfile

# Create requirements.txt
pip freeze > requirements.txt

# Deploy
heroku create your-app-name
git add .
git commit -m "Deploy API"
git push heroku main
```

#### Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

#### Render
```bash
# Create render.yaml
services:
  - type: web
    name: llm-insurance-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn run_public_server:app --host 0.0.0.0 --port $PORT
```

## 📊 API Endpoints

Once publicly accessible, your API will have these endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint with system info |
| GET | `/health` | Health check |
| POST | `/upload/` | Upload insurance documents |
| POST | `/query/` | Submit structured queries |
| POST | `/nl_query/` | Submit natural language queries |
| GET | `/files/` | List uploaded files |
| DELETE | `/files/{file_id}` | Delete uploaded file |
| GET | `/docs` | Interactive API documentation |

## 🔍 Testing the Public API

### Health Check
```bash
curl -X GET "https://your-public-url.com/health"
```

### Upload Document
```bash
curl -X POST "https://your-public-url.com/upload/" \
  -F "file=@documents/sample_policy.pdf"
```

### Submit Query
```bash
curl -X POST "https://your-public-url.com/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "your_file_id",
    "age": 35,
    "gender": "male",
    "procedure": "knee surgery",
    "location": "Mumbai",
    "policy_duration_months": 12
  }'
```

### Natural Language Query
```bash
curl -X POST "https://your-public-url.com/nl_query/" \
  -H "Content-Type: application/json" \
  -d '{
    "file_id": "your_file_id",
    "query_text": "A 35-year-old male wants to claim for knee surgery in Mumbai"
  }'
```

## 🔒 Security Considerations

### For Production Deployment

1. **Add Authentication:**
   ```python
   from fastapi import Depends, HTTPException, status
   from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
   
   security = HTTPBearer()
   
   async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
       if credentials.credentials != "your-secret-token":
           raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
       return credentials.credentials
   ```

2. **Rate Limiting:**
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   from slowapi.errors import RateLimitExceeded
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
   ```

3. **CORS Configuration:**
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

## 📈 Monitoring and Logging

### Add Logging
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Status: {response.status_code}")
    return response
```

### Health Monitoring
```python
@app.get("/metrics")
async def get_metrics():
    return {
        "uptime": time.time() - start_time,
        "requests_processed": request_count,
        "active_connections": active_connections
    }
```

## 🚨 Troubleshooting

### Common Issues

1. **Port Already in Use:**
   ```bash
   # Find process using port 8000
   lsof -i :8000
   
   # Kill the process
   kill -9 <PID>
   
   # Or use different port
   PORT=8080 python run_public_server.py
   ```

2. **CORS Issues:**
   - Ensure CORS middleware is properly configured
   - Check if your frontend domain is in allowed origins

3. **File Upload Issues:**
   - Check file size limits
   - Verify supported file types
   - Ensure proper multipart form data

4. **Memory Issues:**
   - Monitor memory usage
   - Implement file cleanup
   - Consider using external storage

### Debug Mode
```bash
# Enable debug logging
uvicorn run_public_server:app --host 0.0.0.0 --port 8000 --log-level debug
```

## 📋 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8000` | Server port |
| `HOST` | `0.0.0.0` | Server host |
| `LOG_LEVEL` | `info` | Logging level |
| `CORS_ORIGINS` | `*` | Allowed CORS origins |

## 🎯 Production Checklist

- [ ] Add authentication/authorization
- [ ] Implement rate limiting
- [ ] Set up proper CORS configuration
- [ ] Add request logging
- [ ] Set up monitoring and alerting
- [ ] Configure SSL/TLS certificates
- [ ] Set up backup and recovery
- [ ] Implement proper error handling
- [ ] Add API versioning
- [ ] Set up CI/CD pipeline

## 🔗 Quick Start Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start server
python run_public_server.py

# 3. In another terminal, create public URL
ngrok http 8000

# 4. Test the public URL
curl -X GET "https://your-ngrok-url.ngrok.io/health"
```

## 📞 Support

For issues and questions:
1. Check the logs for error messages
2. Test endpoints individually
3. Verify network connectivity
4. Check firewall settings
5. Review security configurations

## 🎉 Success!

Once deployed, your API will be publicly accessible and ready to handle insurance claim evaluations from anywhere in the world!

