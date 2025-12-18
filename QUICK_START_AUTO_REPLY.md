# 🚀 Gmail Auto-Reply Quick Start

## Setup (One-time)

1. **Get Gmail App Password**
   - Visit: https://myaccount.google.com/security
   - Enable 2-Step Verification
   - Create App Password → Mail
   - Copy 16-character code

2. **Create `.env` file**
   ```env
   GMAIL_USER=your_email@gmail.com
   GMAIL_PASSWORD=abcd efgh ijkl mnop
   GROQ_API_KEY=your_groq_key
   ```

## Run Both Servers

**Terminal 1 - Backend:**
```powershell
cd "C:\Users\user\Downloads\AUTO_COLD MAIL GEN\AUTO_COLD MAIL GEN\backend"
python start_server.py
```

**Terminal 2 - Frontend:**
```powershell
cd "C:\Users\user\Downloads\AUTO_COLD MAIL GEN\AUTO_COLD MAIL GEN\mailgen_frontend"
flutter run -d chrome
```

## Send Email with Auto-Reply

1. **AI Gen Tab** → Generate email
2. Enter receiver email
3. ✅ Check **"Enable Auto-Reply"**
4. Click **Send**
5. Note conversation ID

## Monitor Conversations

1. **Threads Tab** → View all conversations
2. Click conversation → See full thread
3. Messages show as:
   - 🔵 Blue bubble = Sent by you
   - ⚪ Grey bubble = Received reply
   - 🟢 Green border = AI auto-reply

## Test Auto-Reply

```powershell
cd "C:\Users\user\Downloads\AUTO_COLD MAIL GEN\AUTO_COLD MAIL GEN"
python test_auto_reply.py
```

Follow prompts to:
- Send test email with auto-reply enabled
- Verify conversation created
- Get instructions for manual reply test

## How It Works

```
Send Email (with auto-reply ✓)
    ↓
System monitors Gmail inbox via IMAP
    ↓
Reply detected (every 60 seconds check)
    ↓
AI generates contextual response
    ↓
Auto-sends reply via Gmail SMTP
    ↓
Tracks in conversation history
    ↓
Continues monitoring for next reply
```

## API Endpoints

```bash
# Send with auto-reply
curl -X POST http://localhost:8000/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": "recipient@example.com",
    "subject": "Test",
    "body": "Hello",
    "from": "your_email@gmail.com",
    "password": "your_app_password",
    "auto_reply_enabled": true
  }'

# List conversations
curl http://localhost:8000/conversations

# Get conversation details
curl http://localhost:8000/conversations/{uuid}

# Toggle auto-reply
curl -X POST http://localhost:8000/conversations/{uuid}/toggle \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No conversations yet" | Send email with auto-reply ✓ first |
| "Failed to send" | Check Gmail credentials in .env |
| "Auto-reply not working" | Verify IMAP enabled in Gmail settings |
| Backend not starting | Install: `pip install -r requirements_full.txt` |
| Frontend not building | Run: `flutter pub get` |

## Important Notes

- ⏱️ **Check interval**: 60 seconds (configurable in `email_monitor.py`)
- 📧 **Daily limit**: 500 emails (Gmail), 2000 (Workspace)
- 🔐 **Security**: Use App Passwords, not regular password
- 💾 **Storage**: Conversations saved in `conversations.json`
- 🤖 **AI Model**: Groq llama-3.1-8b-instant

## Files Modified

✅ Core system already integrated with Gmail IMAP/SMTP
✅ Auto-reply monitoring via background threads
✅ LLM-powered contextual responses
✅ Conversation tracking in JSON
✅ Frontend UI complete

**Ready to use! Just configure credentials and test!** 🎉
