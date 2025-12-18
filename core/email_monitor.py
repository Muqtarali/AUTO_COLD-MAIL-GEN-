"""Email monitoring service for detecting and processing replies."""
import imaplib
import email
from email.header import decode_header
import time
import threading
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class EmailMonitor:
    """Monitors email inbox for replies and triggers auto-response."""
    
    def __init__(self, imap_server='imap.gmail.com', imap_port=993):
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.monitoring_threads = {}
        self.active_conversations = {}
    
    def start_monitoring(
        self,
        conversation_id: str,
        email_address: str,
        password: str,
        original_subject: str,
        recipient_email: str,
        callback
    ):
        """Start monitoring for replies to a specific email thread."""
        if conversation_id in self.monitoring_threads:
            logger.warning(f"Already monitoring conversation {conversation_id}")
            return
        
        # Store conversation metadata
        self.active_conversations[conversation_id] = {
            'email': email_address,
            'recipient': recipient_email,
            'subject': original_subject,
            'last_checked': None,
            'reply_count': 0,
            'processed_uids': set(),  # Track processed messages to avoid double-handling
        }
        
        # Start monitoring thread
        thread = threading.Thread(
            target=self._monitor_inbox,
            args=(conversation_id, email_address, password, original_subject, recipient_email, callback),
            daemon=True
        )
        self.monitoring_threads[conversation_id] = thread
        thread.start()
        logger.info(f"Started monitoring conversation {conversation_id}")
    
    def stop_monitoring(self, conversation_id: str):
        """Stop monitoring a conversation."""
        if conversation_id in self.active_conversations:
            del self.active_conversations[conversation_id]
        if conversation_id in self.monitoring_threads:
            # Thread will exit on next iteration when conversation is not found
            del self.monitoring_threads[conversation_id]
        logger.info(f"Stopped monitoring conversation {conversation_id}")
    
    def _monitor_inbox(
        self,
        conversation_id: str,
        email_address: str,
        password: str,
        original_subject: str,
        recipient_email: str,
        callback
    ):
        """Background thread that monitors inbox for new replies."""
        check_interval = 20  # Check every 20 seconds for faster detection
        
        while conversation_id in self.active_conversations:
            try:
                # Connect to IMAP
                mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
                mail.login(email_address, password)
                mail.select('INBOX')
                
                # Search for ALL emails from recipient (Gmail search is case-insensitive)
                status, messages = mail.search(None, f'FROM "{recipient_email}"')
                
                if status == 'OK':
                    email_ids = messages[0].split()
                    logger.info(
                        f"Monitor {conversation_id}: found {len(email_ids)} total emails from {recipient_email}"
                    )
                    
                    # Check last 50 emails in reverse order (newest first)
                    for email_id in reversed(email_ids[-50:]):
                        # Skip already processed messages
                        if email_id in self.active_conversations[conversation_id]['processed_uids']:
                            continue

                        try:
                            status, msg_data = mail.fetch(email_id, '(RFC822)')
                            
                            if status == 'OK':
                                email_body = msg_data[0][1]
                                message = email.message_from_bytes(email_body)
                                
                                # Extract headers
                                subject = self._decode_header(message.get('Subject', ''))
                                from_header = self._decode_header(message.get('From', ''))
                                in_reply_to = message.get('In-Reply-To', '')
                                
                                # Parse sender email
                                from email.utils import parseaddr
                                sender_email = parseaddr(from_header)[1] or ""
                                
                                # Check if email is a reply
                                is_reply = (
                                    subject.lower().startswith('re:') or 
                                    'fwd' not in subject.lower() and in_reply_to
                                )
                                
                                if is_reply:
                                    logger.info(
                                        f"Monitor {conversation_id}: POTENTIAL REPLY UID {email_id.decode() if isinstance(email_id, bytes) else email_id} "
                                        f"| From={sender_email} | Subject={subject}"
                                    )
                                    
                                    # Extract reply content
                                    reply_text = self._extract_email_body(message)
                                    
                                    if reply_text and len(reply_text.strip()) > 5:
                                        logger.info(
                                            f"Monitor {conversation_id}: MATCHED REPLY from {sender_email} | body_len={len(reply_text)} | Calling callback NOW"
                                        )
                                        # Trigger callback with the reply
                                        callback(conversation_id, sender_email, reply_text)
                                        
                                        # Update conversation state
                                        self.active_conversations[conversation_id]['reply_count'] += 1
                                        self.active_conversations[conversation_id]['last_checked'] = time.time()
                                    else:
                                        logger.warning(f"Monitor {conversation_id}: Reply from {sender_email} has empty/short body")
                                
                                # Mark this UID as processed
                                self.active_conversations[conversation_id]['processed_uids'].add(email_id)
                        except Exception as e:
                            logger.error(f"Monitor {conversation_id}: error processing email_id {email_id}: {e}")
                            # Still mark as processed to avoid re-attempting
                            self.active_conversations[conversation_id]['processed_uids'].add(email_id)
                
                mail.close()
                mail.logout()
                
            except Exception as e:
                logger.error(f"Error monitoring conversation {conversation_id}: {e}", exc_info=True)
            
            # Wait before next check
            time.sleep(check_interval)
            
            # Wait before next check
            time.sleep(check_interval)
    
    def _decode_header(self, header: str) -> str:
        """Decode email header."""
        if not header:
            return ""
        
        decoded_parts = decode_header(header)
        decoded_string = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_string += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_string += part
        
        return decoded_string
    
    def _is_reply_to(self, reply_subject: str, original_subject: str) -> bool:
        """Check if the reply subject matches the original."""
        reply_subject = reply_subject.lower().strip()
        original_subject = original_subject.lower().strip()
        
        # Common reply prefixes
        if reply_subject.startswith('re:'):
            reply_subject = reply_subject[3:].strip()
        if reply_subject.startswith('fwd:'):
            return False  # Ignore forwards
        
        return original_subject in reply_subject or reply_subject in original_subject
    
    def _extract_email_body(self, message) -> str:
        """Extract plain text body from email message."""
        body = ""
        
        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except Exception:
                        pass
        else:
            try:
                body = message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except Exception:
                pass
        
        return body.strip()

# Global monitor instance
_email_monitor = EmailMonitor()

def get_email_monitor() -> EmailMonitor:
    """Get the global email monitor instance."""
    return _email_monitor
