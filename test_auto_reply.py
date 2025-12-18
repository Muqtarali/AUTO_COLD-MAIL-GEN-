"""
Test script for Gmail Auto-Reply functionality.
Run this to verify the entire auto-reply pipeline.
"""
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000"

def test_auto_reply_system():
    """Test the complete auto-reply workflow."""
    
    # Get credentials from environment
    sender_email = os.getenv('GMAIL_USER')
    sender_password = os.getenv('GMAIL_PASSWORD')
    
    if not sender_email or not sender_password:
        print("❌ ERROR: Please set GMAIL_USER and GMAIL_PASSWORD in .env file")
        return
    
    print("🔍 Testing Auto-Reply System")
    print("=" * 50)
    
    # Step 1: Health check
    print("\n1. Checking backend health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("   ✅ Backend is healthy")
        else:
            print(f"   ❌ Backend unhealthy: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Cannot connect to backend: {e}")
        return
    
    # Step 2: Send email with auto-reply enabled
    print("\n2. Sending email with auto-reply enabled...")
    recipient = input("   Enter test recipient email: ").strip()
    if not recipient:
        print("   ❌ No recipient provided")
        return
    
    email_payload = {
        "to": recipient,
        "subject": "Test Auto-Reply System",
        "body": "This is a test email to verify the auto-reply functionality. Please reply to this email to test the automatic response system.",
        "from": sender_email,
        "password": sender_password,
        "auto_reply_enabled": True
    }
    
    try:
        response = requests.post(f"{BASE_URL}/send", json=email_payload)
        if response.status_code == 200:
            result = response.json()
            conversation_id = result.get('conversation_id')
            print(f"   ✅ Email sent successfully")
            print(f"   📧 Conversation ID: {conversation_id}")
            print(f"   🤖 Auto-reply: {result.get('auto_reply_enabled', False)}")
        else:
            print(f"   ❌ Failed to send: {response.json()}")
            return
    except Exception as e:
        print(f"   ❌ Send error: {e}")
        return
    
    # Step 3: Verify conversation was created
    print("\n3. Verifying conversation record...")
    try:
        response = requests.get(f"{BASE_URL}/conversations/{conversation_id}")
        if response.status_code == 200:
            conv = response.json()['conversation']
            print(f"   ✅ Conversation created")
            print(f"   👤 Recipient: {conv.get('recipient_email')}")
            print(f"   📝 Subject: {conv.get('original_subject')}")
            print(f"   🔄 Auto-reply enabled: {conv.get('auto_reply_enabled')}")
            print(f"   💬 Messages: {len(conv.get('messages', []))}")
        else:
            print(f"   ❌ Conversation not found: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 4: List all conversations
    print("\n4. Listing all conversations...")
    try:
        response = requests.get(f"{BASE_URL}/conversations")
        if response.status_code == 200:
            convs = response.json()['conversations']
            print(f"   ✅ Found {len(convs)} conversation(s)")
            for idx, c in enumerate(convs, 1):
                print(f"      {idx}. {c.get('original_subject')} → {c.get('recipient_email')}")
        else:
            print(f"   ❌ Failed to list: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Instructions for manual testing
    print("\n" + "=" * 50)
    print("📋 Next Steps for Manual Testing:")
    print("=" * 50)
    print(f"1. Check email sent to: {recipient}")
    print("2. Reply to that email from the recipient account")
    print("3. Wait 60 seconds for IMAP monitoring to detect reply")
    print("4. Check backend logs for: 'Auto-reply sent for conversation'")
    print("5. Refresh frontend Threads tab to see AI auto-reply")
    print("6. Verify auto-reply has green border in conversation view")
    
    print("\n🔍 Monitor backend logs:")
    print("   cd backend")
    print("   python start_server.py")
    
    print("\n🌐 View in frontend:")
    print("   Navigate to: http://localhost:XXXX/#/")
    print("   Click 'Threads' tab")
    print(f"   Find conversation: '{email_payload['subject']}'")
    
    print("\n✨ Auto-Reply System Test Complete!")

if __name__ == "__main__":
    test_auto_reply_system()
