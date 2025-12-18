"""
Universal Gmail Auto-Reply Monitor
Monitors ALL replies to your sent emails and auto-responds using AI.
"""
import imaplib
import email
import time
import logging
from email.header import decode_header
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from core.llm import generate_reply_to_email
from core.emailer import send_email
import json
from pathlib import Path

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UniversalAutoReplyMonitor:
    """Monitors ALL Gmail replies and auto-responds intelligently."""
    
    def __init__(self):
        self.gmail_user = os.getenv('GMAIL_USER')
        self.gmail_password = os.getenv('GMAIL_PASSWORD')
        self.imap_server = 'imap.gmail.com'
        self.processed_emails_file = Path(__file__).parent / 'processed_emails.json'
        self.processed_emails = self.load_processed_emails()
        self.check_interval = 60  # Check every 60 seconds
        
        if not self.gmail_user or not self.gmail_password:
            raise ValueError("Please set GMAIL_USER and GMAIL_PASSWORD in .env file")
    
    def load_processed_emails(self):
        """Load list of already processed email IDs."""
        if self.processed_emails_file.exists():
            try:
                with open(self.processed_emails_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_processed_emails(self):
        """Save processed email IDs."""
        with open(self.processed_emails_file, 'w') as f:
            json.dump(self.processed_emails, f, indent=2)
    
    def decode_header_value(self, header_value):
        """Decode email header."""
        if not header_value:
            return ""
        
        decoded_parts = decode_header(header_value)
        decoded_string = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_string += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_string += str(part)
        
        return decoded_string
    
    def extract_email_body(self, message):
        """Extract plain text body from email."""
        body = ""
        
        if message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain':
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        pass
        else:
            try:
                body = message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                pass
        
        return body.strip()
    
    def get_sent_email_content(self, subject):
        """Retrieve original sent email content from Sent folder."""
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.gmail_user, self.gmail_password)
            mail.select('"[Gmail]/Sent Mail"')
            
            # Clean subject for search
            search_subject = subject.replace('Re: ', '').replace('RE: ', '').strip()
            
            # Search for sent email with this subject
            status, messages = mail.search(None, f'SUBJECT "{search_subject}"')
            
            if status == 'OK' and messages[0]:
                # Get the most recent sent email
                email_ids = messages[0].split()
                if email_ids:
                    latest_id = email_ids[-1]
                    status, msg_data = mail.fetch(latest_id, '(RFC822)')
                    
                    if status == 'OK':
                        email_body = msg_data[0][1]
                        message = email.message_from_bytes(email_body)
                        original_body = self.extract_email_body(message)
                        
                        mail.close()
                        mail.logout()
                        return original_body
            
            mail.close()
            mail.logout()
        except Exception as e:
            logger.error(f"Error retrieving sent email: {e}")
        
        return "Previous conversation context"
    
    def is_reply_to_my_email(self, message):
        """Check if this is a reply to an email we sent."""
        subject = self.decode_header_value(message.get('Subject', ''))
        
        # Check if it's a reply (starts with Re:)
        if subject.lower().startswith('re:'):
            return True
        
        # Check In-Reply-To and References headers
        in_reply_to = message.get('In-Reply-To')
        references = message.get('References')
        
        return bool(in_reply_to or references)
    
    def monitor_inbox(self):
        """Main monitoring loop - checks inbox for new replies."""
        logger.info("🚀 Starting Universal Auto-Reply Monitor")
        logger.info(f"📧 Monitoring: {self.gmail_user}")
        logger.info(f"⏱️  Check interval: {self.check_interval} seconds")
        logger.info("=" * 60)
        
        while True:
            try:
                self.process_new_replies()
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                logger.info("\n⏹️  Stopping monitor...")
                break
            except Exception as e:
                logger.error(f"❌ Monitor error: {e}")
                time.sleep(self.check_interval)
    
    def process_new_replies(self):
        """Check for and process new replies."""
        try:
            # Connect to Gmail IMAP
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.gmail_user, self.gmail_password)
            mail.select('inbox')
            
            # Search for unread emails from the last 7 days
            since_date = (datetime.now() - timedelta(days=7)).strftime("%d-%b-%Y")
            status, messages = mail.search(None, f'(SINCE {since_date})')
            
            if status != 'OK':
                mail.close()
                mail.logout()
                return
            
            email_ids = messages[0].split()
            new_replies_count = 0
            
            # Process emails in reverse order (newest first)
            for email_id in reversed(email_ids[-20:]):  # Check last 20 emails
                email_id_str = email_id.decode()
                
                # Skip if already processed
                if email_id_str in self.processed_emails:
                    continue
                
                # Fetch email
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                
                if status != 'OK':
                    continue
                
                email_body = msg_data[0][1]
                message = email.message_from_bytes(email_body)
                
                # Check if this is a reply to our email
                if not self.is_reply_to_my_email(message):
                    self.processed_emails[email_id_str] = {
                        'processed_at': datetime.now().isoformat(),
                        'action': 'skipped_not_reply'
                    }
                    continue
                
                # Extract email details
                from_email = email.utils.parseaddr(message.get('From'))[1]
                subject = self.decode_header_value(message.get('Subject', ''))
                reply_body = self.extract_email_body(message)
                
                if not reply_body or len(reply_body) < 10:
                    self.processed_emails[email_id_str] = {
                        'processed_at': datetime.now().isoformat(),
                        'action': 'skipped_empty'
                    }
                    continue
                
                logger.info(f"\n📬 NEW REPLY DETECTED:")
                logger.info(f"   From: {from_email}")
                logger.info(f"   Subject: {subject}")
                logger.info(f"   Preview: {reply_body[:100]}...")
                
                # Get original email content
                original_email = self.get_sent_email_content(subject)
                
                # Generate AI reply
                try:
                    logger.info("   🤖 Generating AI response...")
                    reply_subject, reply_content = generate_reply_to_email(
                        original_email_body=original_email,
                        received_reply=reply_body,
                        conversation_context=""
                    )
                    
                    logger.info(f"   ✅ AI Reply Generated: {reply_content[:100]}...")
                    
                    # Send auto-reply
                    success, error = send_email(
                        smtp_from=self.gmail_user,
                        smtp_password=self.gmail_password,
                        smtp_to=from_email,
                        subject=reply_subject,
                        body=reply_content
                    )
                    
                    if success:
                        logger.info(f"   ✅ AUTO-REPLY SENT to {from_email}")
                        self.processed_emails[email_id_str] = {
                            'processed_at': datetime.now().isoformat(),
                            'action': 'replied',
                            'to': from_email,
                            'subject': subject
                        }
                        new_replies_count += 1
                    else:
                        logger.error(f"   ❌ Failed to send: {error}")
                        self.processed_emails[email_id_str] = {
                            'processed_at': datetime.now().isoformat(),
                            'action': 'failed',
                            'error': str(error)
                        }
                    
                except Exception as e:
                    logger.error(f"   ❌ Error generating reply: {e}")
                    self.processed_emails[email_id_str] = {
                        'processed_at': datetime.now().isoformat(),
                        'action': 'error',
                        'error': str(e)
                    }
            
            # Save processed emails
            self.save_processed_emails()
            
            if new_replies_count > 0:
                logger.info(f"\n✨ Processed {new_replies_count} new reply(ies)")
            else:
                logger.info("✓ No new replies")
            
            mail.close()
            mail.logout()
            
        except Exception as e:
            logger.error(f"❌ Error processing replies: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Start the universal auto-reply monitor."""
    print("=" * 60)
    print("🤖 UNIVERSAL GMAIL AUTO-REPLY MONITOR")
    print("=" * 60)
    print("\nThis will monitor ALL replies to your sent emails")
    print("and automatically respond using AI.\n")
    
    try:
        monitor = UniversalAutoReplyMonitor()
        monitor.monitor_inbox()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease create .env file with:")
        print("GMAIL_USER=your_email@gmail.com")
        print("GMAIL_PASSWORD=your_app_password")
        print("GROQ_API_KEY=your_groq_key")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
