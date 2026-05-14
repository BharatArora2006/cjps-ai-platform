import smtplib
from email.mime.text import MIMEText

import os
from dotenv import load_dotenv

load_dotenv()


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# EMAIL_ADDRESS = "lwilks752@gmail.com"
# EMAIL_PASSWORD = "dzkmjglkabodokam"

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

def send_assignment_email(to_email, contractor_name, job_data):

    subject = f"New Job Assigned - {job_data['county']}"

    body = f'''
Hello {contractor_name},

A new job has been assigned to you.

Client: {job_data['client_name']}
Defendant: {job_data['defendant_name']}
County: {job_data['county']}
Address: {job_data['address']}

Please login to dashboard for details.

Regards,
CJPS System
'''

    msg = MIMEText(body)

    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = to_email

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)

    server.starttls()

    server.login(
        EMAIL,
        PASSWORD
    )

    server.send_message(msg)

    server.quit()

    print("✅ EMAIL SENT")