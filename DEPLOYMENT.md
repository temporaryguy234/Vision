# MotionEdit Deployment Guide

## Overview
MotionEdit is an AI-powered motion graphics template platform that allows users to import, customize, and export Lottie animations. This guide covers deployment using Emergent AI.

## Features
- ✅ Import Lottie JSON and .lottie files from URLs
- ✅ AI-powered natural language editing
- ✅ Client-side preview generation
- ✅ Multi-format export (MP4, WebM, GIF, PNG)
- ✅ User authentication and subscription management
- ✅ Payment integration (Stripe, PayPal)

## Quick Start

### 1. Test the Import Functionality
```bash
# Start the backend server
cd backend
python server.py

# In another terminal, test the import
python test_lottie_import.py
```

### 2. Deploy with Emergent AI
```bash
# Install Emergent AI CLI
npm install -g @emergent-ai/cli

# Login to Emergent AI
emergent login

# Deploy the application
emergent deploy --config emergent-config.yaml
```

## Environment Variables

Set these environment variables in your Emergent AI dashboard:

```env
# Database
MONGO_URL=mongodb://your-mongo-connection-string

# JWT Authentication
JWT_SECRET=your-super-secret-jwt-key

# Backend URL (will be provided by Emergent AI)
BACKEND_URL=https://api.motionedit.com

# Payment Processing
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_CLIENT_SECRET=your-paypal-secret

# AI Services
OPENAI_API_KEY=sk-...
```

## Testing the Import Feature

### Test with the provided Lottie file:
```bash
curl -X POST "https://api.motionedit.com/api/test/import-lottie" \
  -F "url=https://lottie.host/85036dbf-44d5-420d-aa24-325988579179/bN9lsInwGh.json"
```

### Expected Response:
```json
{
  "success": true,
  "animation_data": {
    "version": "4.8.0",
    "width": 298,
    "height": 304,
    "frame_rate": 24,
    "duration": 72,
    "layers_count": 2
  },
  "manifest": {
    "text": [],
    "images": [],
    "colors": [...],
    "chart": [],
    "speed": {"min": 0.2, "max": 3.0, "default": 1.0},
    "anchors": [...]
  },
  "message": "Lottie file processed successfully"
}
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (MongoDB)     │
│   Port: 80      │    │   Port: 8001    │    │   Port: 27017   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CDN           │    │   File Storage  │    │   AI Services   │
│   (CloudFront)  │    │   (S3)          │    │   (OpenAI)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Key Improvements Made

### 1. Enhanced Lottie Processing
- Added proper HTTP headers for external requests
- Improved error handling and validation
- Better Lottie structure validation

### 2. Improved Import Flow
- Better URL validation
- Enhanced filename generation
- Proper error messages
- Client-side preview generation

### 3. Security Enhancements
- Restricted CORS origins
- Better input validation
- Proper error handling

### 4. Deployment Ready
- Docker configuration
- Emergent AI deployment config
- Environment variable management
- Health checks and monitoring

## Troubleshooting

### Import Issues
1. **CORS Errors**: Check that the CORS origins are properly configured
2. **Network Timeouts**: Increase timeout values in the Lottie processor
3. **Invalid JSON**: Ensure the URL returns valid Lottie JSON

### Deployment Issues
1. **Environment Variables**: Verify all required env vars are set
2. **Database Connection**: Check MongoDB connection string
3. **File Permissions**: Ensure upload directories are writable

## Monitoring

The application includes:
- Health check endpoint: `/health`
- Test endpoint: `/api/test/import-lottie`
- Comprehensive logging
- Error tracking

## Support

For issues or questions:
1. Check the logs in Emergent AI dashboard
2. Test the import functionality with the test script
3. Verify environment variables are set correctly
4. Check database connectivity

## Next Steps

After successful deployment:
1. Set up monitoring and alerts
2. Configure CDN for file serving
3. Set up automated backups
4. Implement rate limiting
5. Add comprehensive testing
