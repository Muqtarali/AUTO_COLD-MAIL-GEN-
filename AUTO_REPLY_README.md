# Auto-Reply Email System

## Overview
The Auto-Reply system enables intelligent two-way email communication. When enabled, the system automatically monitors your inbox for replies to sent emails and uses AI to generate and send contextually appropriate responses.

## Features

### 1. **Automatic Email Monitoring**
- Background IMAP monitoring for incoming replies
- Subject-based thread detection
- Automatic email body extraction (supports both plain text and HTML)

### 2. **AI-Powered Reply Generation**
- Uses Groq LLM (llama-3.1-8b-instant) to generate intelligent responses
- Context-aware: considers original email, received reply, and full conversation history
- Professional tone maintained across all auto-replies

### 3. **Conversation Tracking**
- Complete message history stored in JSON format
- Tracks sent emails, received replies, and auto-generated responses
- Enable/disable auto-reply per conversation

### 4. **Frontend UI**
- **Generate Email Screen**: Toggle auto-reply when sending emails
- **Conversation Screen**: View all active conversations, message threads, and auto-reply status
- Real-time status indicators (ACTIVE/PAUSED)
- Manual override: pause/resume auto-reply anytime

## Architecture

### Backend Components

#### 1. Email Monitor (`core/email_monitor.py`)
```python
EmailMonitor.start_monitoring(
    sender_email: str,
    subject: str,
    callback: Callable[[str], None]
)
```
- **Purpose**: Background IMAP monitoring service
- **How it works**:
  - Connects to Gmail via IMAP SSL
  - Runs monitoring loop in daemon thread (checks every 60 seconds)
  - Detects replies by matching "Re:" subject patterns
  - Extracts email body and triggers callback
- **Thread safety**: Uses separate daemon threads per conversation

#### 2. Conversation Store (`core/conversation_store.py`)
```python
create_conversation(conversation_id, to, subject, initial_message)
add_message_to_conversation(conversation_id, message)
get_conversation(conversation_id)
list_conversations()
toggle_auto_reply(conversation_id, enabled)
```
- **Purpose**: JSON-based conversation persistence
- **Storage**: `conversations.json` in workspace root
- **Schema**:
  ```json
  {
    "conversation_id": {
      "id": "uuid",
      "to": "recipient@example.com",
      "subject": "Email subject",
      "auto_reply_enabled": true,
      "messages": [
        {
          "from": "sender@example.com",
          "to": "recipient@example.com",
          "subject": "Re: Email subject",
          "body": "Message content",
          "timestamp": "2024-01-15T10:30:00",
          "type": "sent|received|auto_reply"
        }
      ]
    }
  }
  ```

#### 3. LLM Reply Generation (`core/llm.py`)
```python
generate_reply_to_email(
    original_email_body: str,
    received_reply: str,
    conversation_context: str = ""
) -> str
```
- **Purpose**: AI-powered contextual reply generation
- **Model**: Groq llama-3.1-8b-instant
- **Prompt Engineering**:
  - Maintains professional tone
  - References conversation context
  - Generates specific, actionable responses
  - Avoids generic statements

#### 4. API Endpoints (`backend/app.py`)

**POST /send**
```json
{
  "to": "recipient@example.com",
  "subject": "Email subject",
  "body": "Email body",
  "auto_reply_enabled": true
}
```
Response:
```json
{
  "status": "sent",
  "conversation_id": "uuid-here"
}
```

**GET /conversations**
- Returns list of all conversations with auto-reply enabled

**GET /conversations/{conversation_id}**
- Returns full conversation thread with all messages

**POST /conversations/{conversation_id}/toggle**
```json
{
  "enabled": true
}
```
- Enable/disable auto-reply for specific conversation

### Frontend Components

#### 1. Generate Email Screen (`screens/generate_email_screen.dart`)
- **Auto-Reply Toggle**: Checkbox to enable monitoring when sending
- **Receiver Email Input**: Validates email format
- **Send Button**: Creates conversation and starts monitoring if enabled
- **Success Message**: Shows conversation ID and monitoring status

#### 2. Conversation Screen (`screens/conversation_screen.dart`)
- **Conversation List**: 
  - Shows all active conversations
  - Status indicators (ACTIVE/PAUSED)
  - Message count
  - Last message preview
  - Timestamp

- **Conversation Detail View**:
  - Full message thread
  - Message bubbles with type indicators (Sent/Received/AI Auto-Reply)
  - Toggle auto-reply button
  - Refresh to see new messages
  - Visual distinction for AI-generated replies (green border)

#### 3. API Service (`services/api_service.dart`)
```dart
sendEmail({
  required String to,
  required String subject,
  required String body,
  bool autoReplyEnabled = false,
})

listConversations()
getConversation(String conversationId)
toggleAutoReply(String conversationId, bool enabled)
```

## Setup Instructions

### Prerequisites
1. Gmail account with App Password (for IMAP access)
2. Groq API key
3. Python 3.8+
4. Flutter 3.x

### Backend Setup

1. **Install Dependencies**:
```bash
cd "AUTO_COLD MAIL GEN"
pip install -r requirements_full.txt
```

2. **Configure Environment Variables**:
Create `.env` file:
```env
GROQ_API_KEY=your_groq_api_key_here
GMAIL_USER=your_email@gmail.com
GMAIL_PASSWORD=your_app_password_here
```

3. **Gmail App Password**:
   - Go to Google Account → Security → 2-Step Verification
   - Enable 2-Step Verification if not already enabled
   - Go to App Passwords → Generate new app password
   - Copy 16-character password (no spaces)

4. **Run Backend**:
```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Install Dependencies**:
```bash
cd mailgen_frontend
flutter pub get
```

2. **Run Frontend**:
```bash
# For web:
flutter run -d chrome

# For Windows:
flutter run -d windows
```

## Usage Flow

### Sending Email with Auto-Reply

1. Navigate to "AI Gen" screen
2. Select Resume and Job Description
3. Click "Generate Email"
4. Enter receiver email address
5. **Check "Enable Auto-Reply" checkbox**
6. Click "Send"
7. System creates conversation and starts monitoring

### Monitoring Conversations

1. Navigate to "Threads" screen
2. View all active conversations
3. Click on conversation to see full thread
4. Messages are color-coded:
   - Blue: Your sent messages
   - Grey: Received replies
   - Blue with green border: AI auto-replies

### Managing Auto-Reply

- **Pause**: Click pause button in conversation detail view
- **Resume**: Click play button to re-enable monitoring
- **Manual Check**: Pull to refresh on conversation list/detail

## Auto-Reply Flow Diagram

```
┌─────────────────┐
│  Send Email     │
│ (Auto-Reply ON) │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ Create Conversation ID  │
│ Store Initial Message   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Start IMAP Monitoring   │
│ (Background Thread)     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ Check Inbox Every 60s   │
│ for "Re: Subject"       │
└────────┬────────────────┘
         │
         ▼
    ┌────────────┐
    │Reply Found?│
    └──┬─────┬───┘
       │     │
      Yes    No (continue monitoring)
       │
       ▼
┌──────────────────────┐
│ Extract Reply Body   │
│ Save as "received"   │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────────────┐
│ LLM: Generate Reply          │
│ Context: Original + Reply +  │
│          Conversation        │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────┐
│ Send Auto-Reply      │
│ Save as "auto_reply" │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│ Continue Monitoring  │
│ (for next reply)     │
└──────────────────────┘
```

## Configuration

### Email Monitoring Settings
Edit `core/email_monitor.py`:
```python
# Check interval (seconds)
time.sleep(60)  # Change to desired interval

# IMAP server
imap = imaplib.IMAP4_SSL('imap.gmail.com')  # Change for other providers
```

### LLM Settings
Edit `core/llm.py`:
```python
# Model
model="llama-3.1-8b-instant"  # Change model

# Temperature
temperature=0.7  # Adjust creativity (0.0-1.0)

# Max tokens
max_tokens=500  # Adjust response length
```

### Conversation Storage
Edit `core/conversation_store.py`:
```python
# Storage file location
CONVERSATIONS_FILE = "conversations.json"  # Change path if needed
```

## Troubleshooting

### Email Not Monitoring
1. Check Gmail credentials in .env file
2. Verify App Password is correct (not regular password)
3. Check IMAP is enabled in Gmail settings
4. Review backend logs for IMAP connection errors

### Auto-Reply Not Sending
1. Verify SMTP credentials (uses same Gmail credentials)
2. Check Groq API key is valid
3. Review conversation status (ensure auto_reply_enabled is true)
4. Check backend logs for LLM generation errors

### Conversations Not Showing in Frontend
1. Verify backend is running (http://localhost:8000/health)
2. Check browser console for API errors
3. Refresh conversation list
4. Verify conversation was created with auto_reply_enabled flag

### IMAP Connection Issues
- **Gmail**: Enable "Less secure app access" or use App Password
- **Other providers**: Update IMAP server in email_monitor.py
- **Firewall**: Ensure port 993 (IMAP SSL) is open

## Security Considerations

### Current Limitations
⚠️ **Important**: Email credentials are currently stored in environment variables and passed to monitoring callbacks. For production:
- Implement secure credential storage (e.g., OS keychain)
- Use OAuth2 for Gmail instead of App Passwords
- Encrypt conversation data at rest
- Add authentication/authorization to API endpoints

### Best Practices
- Use App Passwords, never regular Gmail password
- Rotate App Passwords regularly
- Limit monitoring to specific email threads
- Review and audit auto-sent emails periodically
- Set up alerts for monitoring failures

## Performance

### Resource Usage
- **Memory**: ~50-100MB per active monitoring thread
- **CPU**: Minimal (polling every 60s)
- **Network**: 1-2 IMAP requests per minute per conversation

### Scalability
- Current design: Suitable for 10-50 concurrent conversations
- For higher scale: Consider message queue (Redis/RabbitMQ) + worker pool
- Database: Replace JSON file with PostgreSQL/MongoDB for production

### Optimization Tips
- Increase monitoring interval if volume is low
- Use connection pooling for IMAP
- Implement exponential backoff for failed connections
- Cache Groq LLM responses for similar queries

## Future Enhancements

### Planned Features
- [ ] Sentiment analysis on received replies
- [ ] Custom reply templates per conversation
- [ ] Multi-language support
- [ ] Reply tone adjustment (formal/casual)
- [ ] Scheduled auto-reply (business hours only)
- [ ] Email attachment handling
- [ ] CRM integration
- [ ] Analytics dashboard (response rates, sentiment trends)

### Advanced Features
- [ ] Multi-provider support (Outlook, Yahoo, etc.)
- [ ] Webhook notifications for new replies
- [ ] A/B testing for reply strategies
- [ ] Machine learning reply quality scoring
- [ ] Conversation summarization
- [ ] Automatic follow-up scheduling

## API Reference

See [API_REFERENCE.md](API_REFERENCE.md) for detailed endpoint documentation.

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or contributions:
- GitHub Issues: [Create Issue](https://github.com/yourusername/mailgen/issues)
- Email: your.email@example.com
