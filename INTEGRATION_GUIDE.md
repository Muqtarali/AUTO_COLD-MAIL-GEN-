# MailGen Flutter + Python Integration Guide

## Overview
This guide explains how the Flutter frontend integrates with the Python backend API for the MailGen application.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Flutter Frontend                         │
│  (Flutter App - Desktop, Web, Mobile)                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                    HTTP/HTTPS API
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────▼──────────────┐          ┌────────────▼──────────┐
│   FastAPI Backend    │          │    Flask Backend      │
│   (Port 8000)        │          │    (Port 5000)        │
└───────┬──────────────┘          └────────────┬──────────┘
        │                                      │
        └──────────────────┬──────────────────┘
                          │
            ┌─────────────┴────────────┐
            │                          │
    ┌───────▼─────────┐     ┌─────────▼──────────┐
    │ Core Python     │     │  External Services │
    │ Modules         │     │  - Gmail           │
    │ - parsers       │     │  - LLM APIs        │
    │ - llm           │     │  - Storage         │
    │ - stores        │     │    (ChromaDB)      │
    │ - emailer       │     │                    │
    └─────────────────┘     └────────────────────┘
```

## API Communication Flow

### 1. Resume Upload Flow
```
Flutter App
    ↓
[File Picker] → Select resume.pdf
    ↓
[API Service] → POST /upload/resume
    ↓
Backend (FastAPI/Flask)
    ↓
[Save temporarily] → /upload/resume
    ↓
[Parse PDF] → core.parsers.parse_resume_pdf()
    ↓
[Extract Data] → name, email, skills, education
    ↓
[Store in DB] → ChromaDB (core.stores)
    ↓
[Return Response] → {"ok": true, "id": "uuid", "parsed": {...}}
    ↓
Flutter App
    ↓
[Show Success] → Update UI with resume ID
```

### 2. Email Generation Flow
```
Flutter App
    ↓
[Dashboard] → Select Resume + JD
    ↓
[Generate Button] → POST /generate
    ↓
Backend
    ↓
[Retrieve from DB] → Resume text + JD text
    ↓
[Prepare Prompts] → Extract skills, role, company
    ↓
[Call LLM] → core.llm.generate_cold_email()
    ↓
[Generate] → Subject + Body using Claude/GPT
    ↓
[Return] → {"ok": true, "subject": "...", "body": "..."}
    ↓
Flutter App
    ↓
[Display] → Show email preview
```

### 3. Email Sending Flow
```
Flutter App
    ↓
[Send Form] → Recipient, Subject, Body
    ↓
[Send Button] → POST /send
    ↓
Backend
    ↓
[Validate Input] → Check email format
    ↓
[Send Email] → core.emailer.send_email()
    ↓
[SMTP Server] → Gmail or custom SMTP
    ↓
[Response] → {"ok": true} or error
    ↓
Flutter App
    ↓
[Show Status] → Success/Failure message
```

## File Structure & Correspondence

### Flutter Side

```
lib/
├── main.dart
│   └── App entry point, theme setup, navigation
│
├── services/
│   └── api_service.dart
│       └── HTTP communication with backend
│           ├── uploadResume()
│           ├── uploadJd()
│           ├── generateEmail()
│           ├── sendEmail()
│           └── listResumes() / listJds()
│
├── screens/
│   ├── home_screen.dart
│   │   └── Shows available features
│   ├── dashboard_screen.dart
│   │   └── List resumes and JDs
│   ├── upload_resume_screen.dart
│   │   └── File picker and upload
│   ├── generate_email_screen.dart
│   │   └── Select resume/JD and generate
│   └── send_email_screen.dart
│       └── Compose and send emails
│
├── widgets/
│   ├── feature_card.dart
│   │   └── Reusable card UI component
│   └── document_card.dart
│       └── Display resume/JD information
│
└── config/
    └── api_config.dart
        └── Centralized API configuration
```

### Python Backend Side

```
backend/
├── app.py (FastAPI)
│   ├── @app.post("/upload/resume")
│   │   └── Receives file → Calls core.parsers.parse_resume_pdf()
│   ├── @app.post("/upload/jd")
│   │   └── Receives file → Calls core.parsers.parse_jd_pdf()
│   ├── @app.get("/list/resumes")
│   │   └── Queries ChromaDB → Returns resume list
│   ├── @app.get("/list/jds")
│   │   └── Queries ChromaDB → Returns JD list
│   ├── @app.post("/generate")
│   │   └── Calls core.llm.generate_cold_email()
│   └── @app.post("/send")
│       └── Calls core.emailer.send_email()
│
└── flask_app.py (Alternative Flask backend)
    ├── @app.route("/upload/resume", methods=['POST'])
    ├── @app.route("/upload/jd", methods=['POST'])
    ├── @app.route("/list/resumes", methods=['GET'])
    ├── @app.route("/list/jds", methods=['GET'])
    ├── @app.route("/generate", methods=['POST'])
    └── @app.route("/send", methods=['POST'])

core/
├── parsers.py
│   ├── parse_resume_pdf(data)
│   ├── parse_jd_pdf(data)
│   └── clean_html_text(html)
│
├── llm.py
│   └── generate_cold_email(name, skills, resume_summary, jd_summary, role, company)
│
├── stores.py
│   ├── get_resume_store()
│   ├── get_jd_store()
│   └── upsert_doc(col, _id, text, metadata)
│
└── emailer.py
    └── send_email(from_addr, password, to, subject, body)
```

## API Endpoint Specifications

### Upload Resume
```
POST /upload/resume
Content-Type: multipart/form-data

Request:
  - file: <PDF binary data>

Response (200 OK):
{
  "ok": true,
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "parsed": {
    "name": "John Doe",
    "emails": ["john@example.com"],
    "skills": ["Python", "JavaScript", "React"],
    "education": ["B.S. Computer Science"],
    "experience": "5 years as Senior Developer"
  },
  "message": "Resume uploaded successfully"
}

Error (400):
{
  "error": "PDF parse error: <error message>"
}
```

### List Resumes
```
GET /list/resumes

Response (200 OK):
{
  "ok": true,
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "John Doe",
      "metadata": {
        "emails": ["john@example.com"],
        "skills": ["Python", "JavaScript"],
        "summary": "Experienced software engineer..."
      }
    }
  ]
}
```

### Generate Email
```
POST /generate
Content-Type: application/json

Request:
{
  "resume_id": "550e8400-e29b-41d4-a716-446655440000",
  "jd_id": "660e8400-e29b-41d4-a716-446655440001"
}

Response (200 OK):
{
  "ok": true,
  "subject": "Senior Developer Position at Tech Corp",
  "body": "Dear Hiring Manager,\n\nI am writing to express my interest..."
}

Error (404):
{
  "error": "Resume not found"
}
```

### Send Email
```
POST /send
Content-Type: application/json

Request:
{
  "to": "recipient@example.com",
  "subject": "Your Subject Here",
  "body": "Email body content...",
  "from": "sender@gmail.com",
  "password": "app-password"
}

Response (200 OK):
{
  "ok": true,
  "message": "Email sent successfully"
}

Error (400):
{
  "error": "to, subject, and body are required"
}
```

## Data Flow Examples

### Example 1: Complete Resume Upload & Processing

```dart
// Flutter Side
final apiService = ApiService();
final fileBytes = await File(path).readAsBytes();
final result = await apiService.uploadResume(fileBytes, 'resume.pdf');

// Result: {
//   "ok": true,
//   "id": "123e4567-e89b-12d3-a456-426614174000",
//   "parsed": {
//     "name": "Alice Johnson",
//     "skills": ["Python", "AWS"]
//   }
// }

// Store resume ID for later use
final resumeId = result['id'];
```

```python
# Backend Side
@app.post("/upload/resume")
async def upload_resume(file: UploadFile = File(...)):
    data = await file.read()
    
    # Parse resume
    parsed = parse_resume_pdf(data)  # {"name": "Alice Johnson", ...}
    
    # Generate UUID
    _id = str(uuid.uuid4())  # "123e4567-e89b-12d3-a456-426614174000"
    
    # Prepare metadata
    metadata = {
        "name": parsed.get("name"),
        "skills": parsed.get("skills"),
        "summary": text[:500]
    }
    
    # Store in ChromaDB
    col = get_resume_store()
    upsert_doc(col, _id, text, metadata)
    
    # Return response
    return {"ok": True, "id": _id, "parsed": parsed}
```

### Example 2: Email Generation

```dart
// Flutter Side - Select resume and JD, generate email
final result = await apiService.generateEmail(resumeId, jdId);

// Result: {
//   "subject": "Applying for Senior Developer Role",
//   "body": "Dear Hiring Manager,\n\nI am very interested..."
// }

// Display to user
setState(() {
  _generatedSubject = result['subject'];
  _generatedBody = result['body'];
});
```

```python
# Backend Side
@app.post("/generate")
def generate_email(payload: Dict[str, Any]):
    resume_id = payload.get("resume_id")
    jd_id = payload.get("jd_id")
    
    # Retrieve from storage
    resume_doc = get_resume_store().get(ids=[resume_id])
    jd_doc = get_jd_store().get(ids=[jd_id])
    
    # Extract data
    candidate_name = resume_doc["metadatas"][0]["name"]
    resume_skills = resume_doc["metadatas"][0]["skills"]
    jd_role = jd_doc["metadatas"][0]["role"]
    jd_summary = jd_doc["documents"][0][:400]
    
    # Generate email using LLM
    subject, body = generate_cold_email(
        candidate_name,
        ", ".join(resume_skills),
        resume_doc["documents"][0][:400],
        jd_summary,
        jd_role,
        ""
    )
    
    return {"ok": True, "subject": subject, "body": body}
```

## Error Handling

### Common Errors & Solutions

#### 1. Connection Error
```dart
// Flutter catches this
try {
  await apiService.health();
} catch (e) {
  // Show error: "Backend Disconnected"
}
```

#### 2. File Upload Error
```python
# Backend returns error
if not file.filename.lower().endswith('.pdf'):
    return {"error": "Only PDF files are allowed"}, 400
```

```dart
// Flutter handles error
try {
  await uploadResume(bytes, fileName);
} catch (e) {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(content: Text('Upload failed: $e'))
  );
}
```

#### 3. Missing Data Error
```python
# Backend validation
if not rdoc or not rdoc.get('documents'):
    return {"error": "Resume not found"}, 404
```

## Environment Configuration

### Development
```
Flutter API: http://localhost:8000 (or 5000 for Flask)
Backend: Same machine or local network
Debugging: Enabled
CORS: Allow all origins
```

### Production
```
Flutter API: https://api.mailgen.hiresense.com
Backend: Cloud server (AWS, Azure, GCP)
Debugging: Disabled
CORS: Specific origin only
HTTPS: Enabled
```

## Performance Optimization

### Frontend
- Use Provider for state management
- Cache API responses
- Implement pagination for large lists
- Lazy load screens

### Backend
- Use ChromaDB vector indexing
- Implement caching with Redis
- Use async operations
- Batch process emails

## Security Best Practices

### In Development
- ✅ Allow all CORS for local testing
- ✅ Plain HTTP is acceptable
- ✅ No authentication required

### In Production
- 🔒 Use HTTPS only
- 🔒 Implement JWT authentication
- 🔒 Validate all inputs
- 🔒 Use environment variables for secrets
- 🔒 Implement rate limiting
- 🔒 Add request signing
- 🔒 Enable CORS for specific domains only

## Testing the Integration

### 1. Health Check
```bash
curl http://localhost:8000/health
# Response: {"status": "ok"}
```

### 2. Upload Test
```bash
curl -X POST -F "file=@resume.pdf" http://localhost:8000/upload/resume
```

### 3. List Test
```bash
curl http://localhost:8000/list/resumes
```

## Troubleshooting

### Issue: Backend not responding
- Check if backend server is running
- Verify correct port (8000 for FastAPI, 5000 for Flask)
- Check firewall settings
- Verify API URL in Flutter

### Issue: File upload fails
- Check file size (max 16MB)
- Ensure file is PDF format
- Check backend logs for errors
- Verify file permissions

### Issue: Email generation fails
- Ensure both resume and JD are uploaded
- Check if LLM API is configured
- Verify enough tokens available
- Check backend logs

## Next Steps

1. Deploy backend to cloud (AWS, Azure, GCP, Heroku)
2. Implement user authentication
3. Add email tracking
4. Integrate with CRM systems
5. Add analytics dashboard
6. Deploy Flutter to production app stores

## Support

For integration issues, check:
1. Backend logs: `backend.log`
2. Flutter debug console: `flutter run -v`
3. Network requests: Use Chrome DevTools or similar
4. API response: Print response bodies for debugging
