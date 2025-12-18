"""
Manual Reply Generator for existing email threads.
Use this when you receive a reply but didn't send original email through the system.
"""
import os
from dotenv import load_dotenv
from core.llm import generate_reply_to_email
from core.emailer import send_email

load_dotenv()

def send_manual_reply():
    """Generate and send a reply to Kartikey Shukla's email."""
    
    # Original email you sent
    original_email = """
    Dear Hiring Team,

    I am writing to express my strong interest in the **Web Development Intern** position at **Flikt Technology**. As a passionate B.Tech Computer Science student at Sharda University with hands-on experience in modern web technologies, I believe I am well-suited for this role.

    ### Relevant Skills and Experience
    - **Front-End Development:** Proficient in React.js, HTML, CSS, and JavaScript for building responsive, user-friendly interfaces.
    - **Back-End Development:** Experienced with Node.js, Express.js, and Firebase for building robust server-side applications.
    - **Version Control & Collaboration:** Familiar with Git and GitHub for collaborative development and code management.
    - **Problem-Solving:** Strong algorithmic thinking honed through competitive programming and project development.

    ### Academic Background
    I am currently pursuing my **B.Tech in Computer Science** (graduating 2026) with a focus on full-stack development, database management, and software engineering principles.

    ### Additional Strengths
    Strong teamwork, problem-solving abilities, and a proven record of meeting deadlines—qualities I honed through extracurricular activities such as ISRO journal contributions and completing the Oracle Academy Python Pro Bootcamp.

    ### Alignment with Flikt Technology
    Your focus on delivering cutting-edge web solutions aligns perfectly with my passion for building intuitive, high-performance front-end applications. I am eager to bring my technical expertise and creative problem-solving mindset to your development team and contribute to Flikt's growth.

    ### Availability
    I am an immediate joiner and can relocate to Noida without delay. I meet the eligibility criteria (B.Tech, graduating 2026) and am comfortable with the six-month bond.

    I have attached my résumé for your review and would welcome the opportunity to discuss how my background can add value to Flikt Technology. Thank you for considering my application.

    Warm regards,
    Muqtar Ali
    """
    
    # Reply received from Kartikey Shukla
    received_reply = "Kindly provide further documents to proceed"
    
    # Your email credentials
    sender_email = os.getenv('GMAIL_USER')
    sender_password = os.getenv('GMAIL_PASSWORD')
    recipient_email = "kartikey.shukla@flikt.in"  # Based on the screenshot
    
    if not sender_email or not sender_password:
        print("❌ ERROR: Please set GMAIL_USER and GMAIL_PASSWORD in .env file")
        print("\nAdd to .env:")
        print("GMAIL_USER=your_email@gmail.com")
        print("GMAIL_PASSWORD=your_16_char_app_password")
        return
    
    print("🤖 Generating AI reply to Kartikey Shukla's message...")
    print(f"📧 Received: '{received_reply}'")
    print()
    
    # Generate professional reply using AI
    try:
        reply_subject, reply_body = generate_reply_to_email(
            original_email_body=original_email,
            received_reply=received_reply,
            conversation_context=""
        )
        
        print("✅ AI Generated Reply:")
        print("=" * 60)
        print(f"Subject: {reply_subject}")
        print()
        print(reply_body)
        print("=" * 60)
        print()
        
        # Ask for confirmation
        confirm = input("Send this reply? (yes/no): ").strip().lower()
        
        if confirm == 'yes':
            print("\n📤 Sending email...")
            success, error = send_email(
                smtp_from=sender_email,
                smtp_password=sender_password,
                smtp_to=recipient_email,
                subject=reply_subject,
                body=reply_body
            )
            
            if success:
                print("✅ Reply sent successfully to kartikey.shukla@flikt.in!")
                print("📧 Check your Gmail Sent folder to confirm")
            else:
                print(f"❌ Failed to send: {error}")
        else:
            print("❌ Reply not sent")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    send_manual_reply()
