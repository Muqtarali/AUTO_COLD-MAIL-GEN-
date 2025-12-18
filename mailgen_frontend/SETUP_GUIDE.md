# MailGen Flutter Frontend - Setup Guide

## Overview
MailGen is an intelligent cold email generation platform powered by HireSense HR Tech. The Flutter frontend provides a beautiful, responsive interface for managing resumes, job descriptions, and generating personalized cold emails.

## Features

### 1. **Home Screen**
- Dashboard overview with quick access to main features
- Backend connection status monitoring
- Quick start guide for new users
- Feature cards for easy navigation

### 2. **Dashboard**
- **Resumes Tab**: View and manage uploaded resumes
- **Job Descriptions Tab**: View and manage uploaded JDs
- Pull-to-refresh functionality
- Document deletion support

### 3. **Upload Screens**
- **Upload Resume**: PDF file picker and upload functionality
- **Upload JD**: Job description PDF upload
- File validation and error handling
- Upload progress indicators

### 4. **Email Generation**
- Select from uploaded resumes and JDs
- AI-powered email generation
- Preview generated subject and body
- Copy and send functionality

## Project Structure

```
mailgen_frontend/
├── lib/
│   ├── main.dart                    # App entry point
│   ├── services/
│   │   └── api_service.dart         # API communication layer
│   ├── screens/
│   │   ├── home_screen.dart         # Home page with features
│   │   ├── dashboard_screen.dart    # Resume and JD management
│   │   ├── upload_resume_screen.dart # Resume upload
│   │   ├── generate_email_screen.dart # Email generation
│   ├── widgets/
│   │   └── feature_card.dart        # Reusable card component
│   └── models/
│       └── (data models here)
├── pubspec.yaml                     # Dependencies
├── analysis_options.yaml            # Lint rules
├── android/                         # Android-specific code
├── ios/                            # iOS-specific code
├── web/                            # Web platform
├── linux/                          # Linux platform
├── macos/                          # macOS platform
└── windows/                        # Windows platform
```

## Installation & Setup

### Prerequisites
- Flutter SDK (3.0+)
- Dart SDK (included with Flutter)
- Python 3.8+ (for backend)

### 1. Flutter Setup

```bash
# Navigate to the Flutter project directory
cd c:\Users\user\Downloads\AUTO_COLD MAIL GEN\AUTO_COLD MAIL GEN\mailgen_frontend

# Get dependencies
flutter pub get

# Run on available device/emulator
flutter run

# Run on specific platform
flutter run -d chrome        # Web
flutter run -d windows       # Windows
flutter run -d macos         # macOS
```

### 2. Backend Setup

#### Option A: FastAPI (FastAPI)
```bash
# Navigate to backend directory
cd c:\Users\user\Downloads\AUTO_COLD MAIL GEN\AUTO_COLD MAIL GEN\backend

# Install dependencies
pip install -r requirements.txt

# Run FastAPI server
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

#### Option B: Flask
```bash
# Navigate to backend directory
cd c:\Users\user\Downloads\AUTO_COLD MAIL GEN\AUTO_COLD MAIL GEN\backend

# Install dependencies
pip install -r requirements.txt

# Run Flask server
python flask_app.py
```

### 3. Configure API Connection

Edit `lib/services/api_service.dart`:

```dart
static const String baseUrl = 'http://localhost:8000'; // For FastAPI
// OR
static const String baseUrl = 'http://localhost:5000'; // For Flask
```

For mobile/emulator testing, use your machine's IP:
```dart
static const String baseUrl = 'http://192.168.1.100:8000';
```

## Dependencies

### Flutter Packages
- `http: ^1.1.0` - HTTP client for API calls
- `provider: ^6.0.0` - State management
- `file_picker: ^6.0.0` - File selection
- `intl: ^0.19.0` - Internationalization
- `google_fonts: ^6.0.0` - Custom fonts

### Python Packages
- `fastapi==0.95.2` - Web framework
- `uvicorn[standard]==0.22.0` - ASGI server
- `flask==3.0.0` - Alternative web framework
- `flask-cors==4.0.0` - CORS support

## API Endpoints

All endpoints are available at `{baseUrl}` with the following routes:

### Health & Status
- `GET /health` - Backend health check
- `GET /ping` - Simple ping
- `GET /stats` - Document statistics

### File Upload
- `POST /upload/resume` - Upload and parse resume PDF
- `POST /upload/jd` - Upload and parse job description PDF

### Data Management
- `GET /list/resumes` - List all stored resumes
- `GET /list/jds` - List all stored JDs
- `POST /store/resume` - Store resume data
- `POST /store/jd` - Store JD data

### Email Generation
- `POST /generate` - Generate cold email
- `POST /send` - Send email

## Usage Guide

### 1. Upload Resume
1. Go to Home screen → Upload Resume
2. Select your resume PDF
3. Click "Upload"
4. Resume is parsed and stored in the database

### 2. Upload Job Description
1. Go to Home screen → Upload JD
2. Select the job description PDF
3. Click "Upload"
4. JD is parsed and stored

### 3. Generate Cold Email
1. Go to Dashboard
2. Click on Generate Email option
3. Select a resume and JD from dropdowns
4. Click "Generate Email"
5. Review the AI-generated subject and body
6. Copy or send directly

### 4. Send Email
1. After generating an email
2. Enter recipient email address
3. (Optional) Add sender email and password for direct sending
4. Click "Send"

## Troubleshooting

### Backend Connection Issues
- **Error**: "Backend Disconnected"
  - Ensure backend server is running
  - Check if API URL is correct
  - Verify firewall isn't blocking the port
  - Check CORS configuration

### File Upload Issues
- **Error**: "Only PDF files are allowed"
  - Ensure you're uploading PDF files only
  - Check file size (max 16MB)

- **Error**: "PDF parse error"
  - PDF might be corrupted
  - Check if PDF contains required information
  - Try re-exporting the PDF

### Email Generation Issues
- **Error**: "Resume not found" or "JD not found"
  - Ensure resume and JD are uploaded first
  - Refresh the dashboard to see latest uploads
  - Check backend logs for parsing errors

## Development

### Adding New Screens
1. Create new file in `lib/screens/`
2. Extend `StatefulWidget` or `StatelessWidget`
3. Update `main.dart` to include the screen
4. Add navigation in `HomePageState`

### Adding New API Endpoints
1. Add method to `ApiService` class
2. Update backend `app.py` or `flask_app.py`
3. Add corresponding UI in Flutter screens

### Testing
```bash
# Run tests
flutter test

# Run with verbose output
flutter run -v
```

## Performance Optimization

- **Lazy Loading**: Screens load data on demand
- **Caching**: API responses are cached using Provider
- **Pagination**: Large lists support pagination
- **Compression**: HTTP requests use gzip compression

## Security Considerations

- ✅ HTTPS support (enable in production)
- ✅ CORS configuration
- ✅ File type validation
- ✅ File size limits
- ✅ Error message sanitization

### For Production
1. Change API URL to HTTPS
2. Implement authentication (JWT tokens)
3. Add request signing
4. Validate all user inputs
5. Use environment variables for secrets

## Deployment

### Flutter Web
```bash
flutter build web --release
# Deploy contents of build/web/ to your hosting
```

### Flutter Windows/macOS/Linux
```bash
flutter build windows --release
flutter build macos --release
flutter build linux --release
```

### Python Backend
```bash
# Using Gunicorn (recommended for production)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Future Enhancements

- [ ] User authentication and accounts
- [ ] Email templates library
- [ ] A/B testing for email variations
- [ ] Analytics and tracking
- [ ] Batch email generation
- [ ] Calendar integration
- [ ] CRM integrations
- [ ] AI model fine-tuning
- [ ] Multi-language support
- [ ] Dark mode theme

## Support & Documentation

- **Flutter Docs**: https://flutter.dev/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Flask Docs**: https://flask.palletsprojects.com/
- **Dart Docs**: https://dart.dev/guides

## License

All rights reserved © HireSense HR Tech

## Contributing

For bug reports and feature requests, please contact the development team.
