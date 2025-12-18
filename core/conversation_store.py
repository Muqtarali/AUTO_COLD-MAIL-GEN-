"""Simple JSON-based conversation storage."""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

CONVERSATIONS_FILE = Path(__file__).parent.parent / "conversations.json"

def load_conversations() -> Dict:
    """Load conversations from JSON file."""
    if not CONVERSATIONS_FILE.exists():
        return {}
    
    try:
        with open(CONVERSATIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}

def save_conversations(conversations: Dict):
    """Save conversations to JSON file."""
    with open(CONVERSATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(conversations, f, indent=2, ensure_ascii=False)

def create_conversation(
    conversation_id: str,
    sender_email: str,
    recipient_email: str,
    original_subject: str,
    original_body: str,
    auto_reply_enabled: bool = True,
    sender_password: str = None
) -> Dict:
    """Create a new conversation entry."""
    conversations = load_conversations()
    
    conversations[conversation_id] = {
        'id': conversation_id,
        'sender_email': sender_email,
        'recipient_email': recipient_email,
        'to': recipient_email,  # For frontend compatibility
        'subject': original_subject,  # For frontend compatibility
        'original_subject': original_subject,
        'original_body': original_body,
        'auto_reply_enabled': auto_reply_enabled,
        'sender_password': sender_password,  # Store for auto-reply (should be encrypted in production)
        'created_at': datetime.now().isoformat(),
        'messages': [
            {
                'from': sender_email,
                'to': recipient_email,
                'subject': original_subject,
                'body': original_body,
                'timestamp': datetime.now().isoformat(),
                'type': 'sent'
            }
        ],
        'status': 'monitoring' if auto_reply_enabled else 'sent'
    }
    
    save_conversations(conversations)
    return conversations[conversation_id]

def add_message_to_conversation(
    conversation_id: str,
    from_email: str,
    to_email: str,
    subject: str,
    body: str,
    message_type: str  # 'received' or 'sent'
):
    """Add a message to an existing conversation."""
    conversations = load_conversations()
    
    if conversation_id not in conversations:
        raise ValueError(f"Conversation {conversation_id} not found")
    
    conversations[conversation_id]['messages'].append({
        'from': from_email,
        'to': to_email,
        'subject': subject,
        'body': body,
        'timestamp': datetime.now().isoformat(),
        'type': message_type
    })
    
    save_conversations(conversations)

def get_conversation(conversation_id: str) -> Optional[Dict]:
    """Get a conversation by ID."""
    conversations = load_conversations()
    return conversations.get(conversation_id)

def list_conversations() -> List[Dict]:
    """List all conversations."""
    conversations = load_conversations()
    return list(conversations.values())

def update_conversation_status(conversation_id: str, status: str):
    """Update conversation status."""
    conversations = load_conversations()
    
    if conversation_id in conversations:
        conversations[conversation_id]['status'] = status
        save_conversations(conversations)

def toggle_auto_reply(conversation_id: str, enabled: bool):
    """Enable or disable auto-reply for a conversation."""
    conversations = load_conversations()
    
    if conversation_id in conversations:
        conversations[conversation_id]['auto_reply_enabled'] = enabled
        save_conversations(conversations)