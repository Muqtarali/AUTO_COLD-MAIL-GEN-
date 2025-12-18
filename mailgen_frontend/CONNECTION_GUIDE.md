# Frontend-Backend Connection Guide

## Connection Architecture

```
Flutter Frontend (Port: Any)
    ↓ HTTP/JSON (http package)
    ↓
FastAPI Backend (Port: 8000)
    ↓
Python Core Modules
    ↓
External Services (Groq LLM, Gmail SMTP, ChromaDB)
```

## Configuration Files

### 1. API Service (`lib/services/api_service.dart`)
- **Base URL:** `http://localhost:8000`
- **HTTP Method:** GET, POST, PUT, DELETE
- **Content-Type:** application/json, multipart/form-data
- **Timeout:** 30 seconds per request

### 2. API Config (`lib/config/api_config.dart`)
- Centralized endpoint definitions
- Base URL configuration
- File upload settings (max 16MB)
- Timeout settings

### 3. Connection Checker (`lib/services/connection_checker.dart`)
- Verifies frontend-backend connectivity
- Tests all API endpoints
- Provides detailed connection status

## Endpoints Status

| Endpoint | Method | Frontend | Backend | Status |
|----------|--------|----------|---------|--------|
| `/health` | GET | ✅ | ✅ | Working |
| `/list/resumes` | GET | ✅ | ✅ | Working |
| `/list/jds` | GET | ✅ | ✅ | Working |
| `/upload/resume` | POST | ✅ | ✅ | Working |
| `/upload/jd` | POST | ✅ | ✅ | Working |
| `/generate` | POST | ✅ | ✅ | Working |
| `/send` | POST | ✅ | ✅ | Working |
| `/stats` | GET | ✅ | ✅ | Working |

## Backend Setup (FastAPI)

### Start Backend Server

```bash
cd AUTO_COLD_MAIL_GEN/backend

# Option 1: Using Python directly
python app.py

# Option 2: Using uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Verify Backend is Running
```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}
```

## Frontend Setup

### 1. Update API Configuration
Edit `lib/config/api_config.dart`:
```dart
// For local development
static const String apiBaseUrl = 'http://localhost:8000';

// For production (when deployed)
// static const String apiBaseUrl = 'https://api.yourdomain.com';
```

### 2. Install Dependencies
```bash
cd mailgen_frontend
flutter pub get
```

### 3. Run Frontend
```bash
flutter run
```

## Testing Connection

### Using Connection Test Screen
1. Open the app
2. Navigate to "Connection Test" screen
3. View live connection status
4. Test all endpoints simultaneously
5. Refresh to retest

### Using curl (Terminal)
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test list resumes
curl http://localhost:8000/list/resumes

# Test list JDs
curl http://localhost:8000/list/jds

# Test stats
curl http://localhost:8000/stats
```

## API Request Examples

### Upload Resume (Flutter)
```dart
final fileBytes = await File(filePath).readAsBytes();
final response = await apiService.uploadResume(fileBytes, 'resume.pdf');
print(response); // {"id": "uuid", "name": "resume.pdf", ...}
```

### Generate Email (Flutter)
```dart
final response = await apiService.generateEmail(resumeId, jdId);
print(response); // {"subject": "...", "body": "...", ...}
```

### Send Email (Flutter)
```dart
final response = await apiService.sendEmail(
  to: 'candidate@example.com',
  subject: 'Job Opportunity',
  body: 'Dear candidate...',
  from: 'hr@company.com',
  password: 'app_password',
);
```

## Data Flow Diagram

```
Frontend Screen → API Service → HTTP Request → Backend Endpoint
                                                     ↓
                                            Python Core Logic
                                                     ↓
                                        External Services (LLM, SMTP)
                                                     ↓
                                            JSON Response ← Backend
                           ← HTTP Response ← 
           ← Parsed JSON ←
```

## Response Format

All endpoints return standardized JSON:

### Success Response (200)
```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation completed"
}
```

### Error Response (4xx/5xx)
```json
{
  "status": "error",
  "detail": "Error description",
  "code": "ERROR_CODE"
}
```

## Troubleshooting

### Issue: "Connection Refused"
**Cause:** Backend not running
**Solution:** 
```bash
cd backend
python app.py
# Check: curl http://localhost:8000/health
```

### Issue: "CORS Error"
**Cause:** Cross-origin restriction
**Solution:** Backend has CORS middleware enabled for all origins (see `app.py`)

### Issue: "Timeout"
**Cause:** Network latency or slow backend
**Solution:** Increase timeout in `api_config.dart`:
```dart
static const int connectTimeout = 60; // increased from 30
```

### Issue: "File Upload Failed"
**Cause:** File too large or wrong format
**Solution:** 
- Max file size: 16MB
- Allowed types: PDF only
- Check file exists before upload

### Issue: "Email Generation Fails"
**Cause:** Groq API key missing or invalid
**Solution:** 
- Verify `GROQ_API_KEY` environment variable in backend
- Check Groq API credentials

## CORS Configuration

Frontend can communicate with backend because:
1. Backend has CORS middleware enabled
2. Allows all origins for development: `allow_origins=["*"]`
3. Allows all methods and headers
4. Change for production in `backend/app.py`

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Network Architecture

### Local Development
```
Frontend: http://localhost:5000 (or debug port)
Backend: http://localhost:8000
Connection: Direct HTTP over localhost
```

### Production
```
Frontend: https://app.mailgen.io
Backend: https://api.mailgen.io
Connection: HTTPS with proper SSL certificates
```

## Security Considerations

1. **HTTPS in Production:** Never use HTTP for production
2. **API Keys:** Store backend API keys in environment variables
3. **SMTP Passwords:** Never hardcode in frontend
4. **CORS:** Restrict to specific domains in production
5. **Rate Limiting:** Implement in production backend

## Monitoring Connection Health

The Connection Checker module provides:
- Real-time connection status
- Endpoint health verification
- Detailed error messages
- Timestamp logging
- Visual status indicators

## Connection Test Results Interpretation

| Status | Meaning | Action |
|--------|---------|--------|
| ✅ Green | Connected | All systems operational |
| ❌ Red | Disconnected | Start backend server |
| ⏱️ Gray | Testing... | Wait for test completion |
| ⚠️ Yellow | Partial | Some endpoints failing |

## Next Steps

1. **Start Backend:** `python app.py`
2. **Verify Connection:** Run connection test
3. **Upload Resume:** Test file upload functionality
4. **Generate Email:** Test LLM integration
5. **Send Email:** Test SMTP configuration

---

**Status:** ✅ Connection Module Complete and Verified
**Last Updated:** December 17, 2025
**Maintainer:** MailGen Team
