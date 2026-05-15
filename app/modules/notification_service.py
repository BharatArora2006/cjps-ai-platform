import os
import resend

from dotenv import load_dotenv

load_dotenv()

# ✅ RESEND API KEY
resend.api_key = os.getenv("RESEND_API_KEY")


def send_assignment_email(
    to_email,
    contractor_name,
    job_data
):

    try:

        subject = (
            f"New Job Assigned - "
            f"{job_data['county']}"
        )

        body = f"""
Hello {contractor_name},

A new job has been assigned to you.

Client: {job_data['client_name']}
Defendant: {job_data['defendant_name']}
County: {job_data['county']}
Address: {job_data['address']}

Please login to dashboard for details.

Regards,
CJPS System
"""

        response = resend.Emails.send({

            "from": "CJPS <onboarding@resend.dev>",

            "to": [to_email],

            "subject": subject,

            "text": body

        })

        print("✅ EMAIL SENT")
        print(response)

    except Exception as e:

        print("❌ EMAIL ERROR:", e)