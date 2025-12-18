# Gmail API Auto-Reply Setup Guide

## Quick Setup Steps

### 1. Get Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to **Security** → **2-Step Verification** (enable if not already enabled)
3. Scroll down to **App passwords**
4. Generate a new app password for "Mail"
5. Copy the 16-character password (no spaces)

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Gmail Credentials for Sending and Monitoring
GMAIL_USER=your_email@gmail.com
GMAIL_PASSWORD=your_16_char_app_password

# Groq API for LLM Auto-Reply Generation
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Send Email with Auto-Reply

When sending an email through the frontend:

1. Navigate to **AI Gen** screen
2. Generate your email
3. Enter receiver email
4. **Check "Enable Auto-Reply" checkbox** ✓
5. Click **Send**

The system will:
- Send the email via Gmail SMTP
- Create a conversation record
- Start IMAP monitoring for replies
- Show conversation in **Threads** tab

### 4. Monitor Auto-Reply Activity

Go to **Threads** tab to:
- View all active conversations
- See message threads
- Pause/resume auto-reply
- Check AI-generated responses (green border)

## How Auto-Reply Works

### Email Monitoring (IMAP)
```
Every 60 seconds:
1. Connect to Gmail via IMAP SSL (port 993)
2. Search inbox for emails FROM recipient
3. Check if subject matches "Re: [original subject]"
4. Extract reply body
5. Trigger auto-response
```

### Auto-Response Flow
```
When reply detected:
1. Add received message to conversation
2. Build context (original email + reply + history)
3. Call Groq LLM to generate contextual response
4. Send auto-reply via Gmail SMTP
5. Add auto-reply to conversation (marked as 'auto_reply' type)
6. Continue monitoring for next reply
```

## Testing End-to-End

### Test Scenario
1. **Send test email** with auto-reply enabled
2. **Reply to that email** from recipient account
3. **Wait 60 seconds** (IMAP check interval)
4. **Check Threads tab** - should see:
   - Original sent message (blue bubble)
   - Received reply (grey bubble)
   - AI auto-reply (blue bubble with green border)

### Debugging

Check backend logs for:
```
INFO:     Started monitoring conversation {uuid}
INFO:     Auto-reply sent for conversation {uuid}
```

Check frontend console for:
```
Error loading conversations: ...
```

## Security Notes

⚠️ **Current Implementation**:
- Passwords stored in conversation JSON (plain text)
- Only suitable for development/testing

✅ **Production Recommendations**:
1. Encrypt passwords at rest
2. Use OAuth2 instead of App Passwords
3. Store credentials in secure vault (e.g., AWS Secrets Manager)
4. Add API authentication
5. Implement rate limiting

## Gmail API Rate Limits

- **IMAP connections**: 15 connections per account
- **Emails sent per day**: 500 (for regular Gmail), 2000 (for Google Workspace)
- **SMTP connections**: Avoid excessive reconnections

## Customization

### Change Monitoring Interval
Edit `core/email_monitor.py`:
```python
check_interval = 60  # Change to desired seconds (e.g., 30, 120)
```

### Customize Reply Tone
Edit `core/llm.py` in `generate_reply_to_email()`:
```python
prompt = f"""... maintain a [FORMAL/CASUAL/FRIENDLY] tone..."""
```

### Enable/Disable for Specific Conversations
Use the toggle button in conversation detail view or API:
```bash
curl -X POST http://localhost:8000/conversations/{id}/toggle \
  -H "Content-Type: application/json" \
  -d '{"enabled": false}'
```

## Troubleshooting

### "Failed to connect to IMAP"
- Verify Gmail App Password is correct
- Check IMAP is enabled in Gmail settings
- Ensure port 993 is not blocked by firewall

### "Auto-reply not sending"
- Check Groq API key is valid
- Verify conversation has `auto_reply_enabled: true`
- Check backend logs for errors
- Ensure sender password is stored in conversation

### "No conversations showing"
- Verify backend is running (http://localhost:8000/health)
- Check conversation was created with auto-reply flag
- Look at browser console for API errors

## Example Usage

```python
# Send email with auto-reply via API
import requests

response = requests.post('http://localhost:8000/send', json={
    'to': 'recipient@example.com',
    'subject': 'Job Application Follow-up',
    'body': 'Dear Hiring Manager, ...',
    'from': 'your_email@gmail.com',
    'password': 'your_app_password',
    'auto_reply_enabled': True
})

print(response.json())
# {'ok': True, 'conversation_id': 'uuid-here', 'auto_reply_enabled': True}

# Check conversation status
conversation_id = response.json()['conversation_id']
conv = requests.get(f'http://localhost:8000/conversations/{conversation_id}')
print(conv.json())
```

## Next Steps

1. **Test basic flow**: Send → Reply → Check auto-response
2. **Monitor logs**: Watch backend for IMAP activity
3. **Customize prompts**: Adjust LLM reply generation
4. **Add security**: Implement credential encryption
5. **Scale**: Add Redis queue for high-volume scenarios
