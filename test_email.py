import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email configuration
smtp_server = "smtp.gmail.com"
smtp_port = 587
sender_email = "your_email@gmail.com"  # <-- Your Gmail address
receiver_email = "your_email@gmail.com"  # <-- Recipient (can be your own)
password = "uzojpvkdupoonewv"  # <-- Your Gmail App Password

# Create the email object
message = MIMEMultipart("alternative")
message["Subject"] = "Test Email from Python"
message["From"] = sender_email
message["To"] = receiver_email

# Plain text version
text = "Hi,\nThis is a test email from Python."
html = """
<html>
  <body>
    <h2 style=\"color: blue;\">Test Email from Python!</h2>
    <p>This email was sent using Gmail SMTP and a Python script.</p>
  </body>
</html>
"""

# Attach both versions
message.attach(MIMEText(text, "plain"))
message.attach(MIMEText(html, "html"))

try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    server.quit()
    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")
