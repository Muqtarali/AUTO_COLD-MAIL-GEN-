# MailGen Flutter App - Quick Reference

## 🎯 Quick Navigation Guide

| Tab | Feature | Purpose |
|-----|---------|---------|
| 🏠 Home | Home Screen | Backend status & overview |
| 📊 Dashboard | Dashboard | View all documents |
| 📄 Resume | Upload Resume | Upload & parse resumes |
| 💼 JD | Upload JD | Upload job descriptions |
| 📧 Generate | Generate Email | AI email creation |
| ✉️ Send | Send Email | SMTP email sending |
| 🔍 Search | Search/Match | Find documents |
| 📈 Stats | Statistics | View analytics |
| 🎯 ATS | ATS Score | Calculate match % |
| 🌐 Scrape | Scrape URL | Extract job postings |

## 📋 Feature Checklist

### ✅ Completed Features
- [x] 10 Full-featured screens
- [x] API integration (9 endpoints)
- [x] Resume upload & parsing
- [x] Job description upload & parsing
- [x] Cold email generation (Groq LLM)
- [x] Email sending (SMTP)
- [x] Document search & filtering
- [x] Statistics dashboard
- [x] ATS score calculation
- [x] URL job scraping
- [x] Error handling
- [x] Loading states
- [x] Empty states
- [x] Bottom navigation (10 tabs)
- [x] Material Design 3 theming

## 🚀 Running the App

### Prerequisites
```bash
flutter --version  # Should be 3.0+
dart --version     # Should be 3.8.1+
```

### Setup
```bash
cd mailgen_frontend
flutter pub get
```

### Run
```bash
flutter run
```

### Build
```bash
# Android APK
flutter build apk --release

# iOS
flutter build ios --release

# Web
flutter build web --release
```

## 🔧 Configuration

### Backend URL
File: `lib/config/api_config.dart`
```dart
static const String baseUrl = 'http://localhost:8000';
```

### API Timeout
```dart
static const Duration timeout = Duration(seconds: 30);
```

### Max File Size
```dart
static const int maxFileSize = 10 * 1024 * 1024; // 10MB
```

## 📱 Screen Details

### Screen 1: Home (Home Screen)
- Shows backend connectivity status
- 4 main feature cards with descriptions
- Quick start guide (4 steps)
- Tap cards to navigate to features

### Screen 2: Dashboard
- Two tabs: Resumes & Job Descriptions
- Shows recent documents
- Pull-to-refresh to reload
- Quick upload buttons

### Screen 3: Upload Resume
- Pick PDF from device
- Automatically extracts:
  - Name, Email, Phone
  - Skills, Experience
  - Education, Certifications
- Shows extraction results
- Save to database

### Screen 4: Upload JD
- Pick or enter job description
- Extract:
  - Role, Company, Location
  - Requirements, Responsibilities
  - Salary range, Job type
- Display parsed results

### Screen 5: Generate Email
- Select resume from dropdown
- Select job description from dropdown
- Click "Generate Email"
- AI generates cold email subject & body
- Copy or send directly

### Screen 6: Send Email
- Enter recipient email
- Edit subject line
- Edit email body
- Optional: Custom sender email
- Optional: App password
- Click Send

### Screen 7: Search & Match
- Tab 1: Search resumes (by name/email/skills)
- Tab 2: Search job descriptions (by role/company)
- Real-time filtering as you type
- Tap result to view details

### Screen 8: Statistics
- Display total counts
- Show recent uploads
- View document metadata
- Refresh to update

### Screen 9: ATS Score
- Select resume from dropdown
- Select job description from dropdown
- Click "Calculate ATS Score"
- Shows:
  - Match percentage (0-100%)
  - Matched skills (green)
  - Missing skills (orange)
  - Visual progress indicator

### Screen 10: Scrape URL
- Enter job posting URL
- Click "Scrape Job Posting"
- Displays:
  - Job title, company, location
  - Salary, employment type
  - Full job description
  - Key requirements (red chips)
  - Nice-to-have skills (yellow chips)
- Save as new job description

## 🎨 Design System

**Colors:**
- Primary: Indigo (#6366F1)
- Success: Green
- Warning: Orange
- Error: Red
- Info: Blue

**Typography:**
- Font: Poppins
- Sizes: 12px (small) → 36px (display)

**Components:**
- ElevatedButton: Primary actions
- OutlinedButton: Secondary actions
- Chips: Tags & filters
- Cards: Content containers
- ListTile: List items

## 🔄 API Endpoints Reference

```
GET  /health                   - Check backend status
POST /upload/resume            - Upload resume PDF
POST /upload/jd                - Upload job description
GET  /list/resumes             - Get all resumes
GET  /list/jds                 - Get all job descriptions
POST /generate                 - Generate cold email
POST /send                     - Send email via SMTP
GET  /stats                    - Get statistics
GET  /search                   - Search documents
```

## 🛠️ Troubleshooting

### App won't compile
```bash
flutter clean
flutter pub get
flutter pub upgrade
flutter run
```

### Backend connection error
- Check backend is running
- Verify API base URL in config
- Check firewall settings
- Test with: `curl http://localhost:8000/health`

### File upload fails
- Ensure file < 10MB
- Use standard PDF format
- Check file permissions

### Email generation timeout
- Verify Groq API key in backend
- Check internet connection
- Increase timeout in config

### Email send fails
- Verify SMTP credentials
- For Gmail: enable "Less secure apps"
- Use app password if 2FA enabled

## 📊 Testing Workflow

1. **Start backend**
   ```bash
   python app.py  # or FastAPI equivalent
   ```

2. **Start app**
   ```bash
   flutter run
   ```

3. **Test flow:**
   - Check Home screen status
   - Upload a test resume
   - Upload a test job description
   - Generate an email
   - View stats and ATS score
   - Try searching

## 📦 Project Structure

```
mailgen_frontend/
├── lib/
│   ├── main.dart                    # Entry point
│   ├── config/
│   │   └── api_config.dart         # Configuration
│   ├── services/
│   │   └── api_service.dart        # API client
│   ├── screens/                    # 10 feature screens
│   │   ├── home_screen.dart
│   │   ├── dashboard_screen.dart
│   │   ├── upload_resume_screen.dart
│   │   ├── upload_jd_screen.dart
│   │   ├── generate_email_screen.dart
│   │   ├── send_email_screen.dart
│   │   ├── search_match_screen.dart
│   │   ├── stats_screen.dart
│   │   ├── ats_score_screen.dart
│   │   └── scrape_jd_url_screen.dart
│   └── widgets/
│       └── feature_card.dart
├── pubspec.yaml                    # Dependencies
├── SETUP_GUIDE.md
├── FEATURES_COMPLETED.md
└── README.md
```

## 💡 Tips & Best Practices

1. **Always check backend status first** - Green indicator means ready
2. **Use real PDFs for testing** - Resume/JD parsing works best with formatted documents
3. **Gmail SMTP tips** - Create an app-specific password, don't use main password
4. **File size limits** - Keep PDFs under 10MB for faster uploads
5. **Search tips** - Case-insensitive, partial matching supported
6. **ATS scoring** - More matched skills = higher score
7. **Email generation** - Better results with complete JD and resume data

## 📚 Documentation Files

- `SETUP_GUIDE.md` - Complete setup instructions
- `FEATURES_COMPLETED.md` - Detailed feature documentation
- `INTEGRATION_GUIDE.md` - Backend integration details
- `README.md` - Quick overview

## 🎓 Learning Resources

- Flutter Docs: https://flutter.dev/docs
- Dart Docs: https://dart.dev/guides
- Provider Package: https://pub.dev/packages/provider
- Material Design 3: https://m3.material.io

## 📞 Support

For issues or questions:
1. Check error messages in console
2. Review troubleshooting section
3. Check backend logs
4. Verify configuration files
5. Test with curl commands

---

**Last Updated:** 2024
**App Version:** 1.0.0
**Status:** ✅ Production Ready
