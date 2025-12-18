# core/llm.py
from typing import Tuple
from groq import Groq
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize Groq client with API key from .env
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def _get_model_name():
    """Return the Groq model name, preferring GROQ_MODEL then MODEL_NAME."""
    return os.environ.get("GROQ_MODEL") or os.environ.get("MODEL_NAME") or "llama-3.3-70b-versatile"

def generate_cold_email(
    name: str,
    skills: str,
    summary: str,
    jd_summary: str,
    role: str,
    portfolio: str
) -> Tuple[str, str]:
    """
    Generates a cold email subject and body using candidate and job info via Groq LLM.
    Returns: (subject, body)
    """

    # Convert skills list to comma-separated string
    if isinstance(skills, list):
        skills = ", ".join(skills)

    # Prompt for Groq
    prompt = f"""
Generate a professional cold email for a recruiter based on this data:

Candidate Name: {name}
Skills: {skills}
Summary: {summary}

Job Role: {role}
Job Description Summary: {jd_summary}

Portfolio Links: {portfolio}

Return the email in this format:
Subject: <subject line>
Body:
<body text>
"""

    model_name = _get_model_name()
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a professional email generator for job applications."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_completion_tokens=1000,
            top_p=1
        )
        output = completion.choices[0].message.content.strip()
    except Exception as e:
        # Return error details for display in Streamlit
        return "Groq API Error", f"Error generating email: {e}"

    # Extract subject & body
    subject, body = "", ""
    if "Subject:" in output:
        parts = output.split("Subject:", 1)[1].strip().split("Body:", 1)
        subject = parts[0].strip()
        if len(parts) > 1:
            body = parts[1].strip()
    else:
        subject = f"Application for {role} - {name}"
        body = output

    return subject, body


def generate_reply_to_email(
    original_email_body: str,
    received_reply: str,
    conversation_context: str = ""
) -> Tuple[str, str]:
    """
    Generates an intelligent reply to a received email using Groq LLM.
    Returns: (subject, body)
    """
    
    prompt = f"""
You are a professional email assistant helping to continue a job application conversation.

Original Email Sent:
{original_email_body}

Reply Received:
{received_reply}

{f"Previous Conversation Context: {conversation_context}" if conversation_context else ""}

Generate a professional, contextual response that:
1. Acknowledges their message appropriately
2. Addresses any questions they asked
3. Shows enthusiasm and professionalism
4. Maintains the conversation naturally
5. Is concise but complete

Return the reply in this format:
Subject: <subject line for the reply>
Body:
<body text>
"""
    
    model_name = _get_model_name()
    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a professional email assistant for job seekers, helping them respond intelligently to recruiter emails."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_completion_tokens=1000,
            top_p=1
        )
        output = completion.choices[0].message.content.strip()
    except Exception as e:
        return "Re: Your Message", f"Thank you for your email. I appreciate your response and would be happy to discuss further.\n\nError generating detailed reply: {e}"
    
    # Extract subject & body
    subject, body = "", ""
    if "Subject:" in output:
        parts = output.split("Subject:", 1)[1].strip().split("Body:", 1)
        subject = parts[0].strip()
        if len(parts) > 1:
            body = parts[1].strip()
    else:
        subject = "Re: Your Message"
        body = output
    
    return subject, body
