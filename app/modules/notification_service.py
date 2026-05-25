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

        html = f"""

        <h2>
        New Job Assigned
        </h2>

        <p>
        Hello {contractor_name},
        </p>

        <p>
        A new job has been assigned to you.
        </p>

        <p>
        <b>Client:</b> {job_data['client_name']}
        </p>

        <p>
        <b>Defendant:</b> {job_data['defendant_name']}
        </p>

        <p>
        <b>County:</b> {job_data['county']}
        </p>

        <p>
        <b>Address:</b> {job_data['address']}
        </p>

        <p>
        Please
        <a
            href="https://cjps-ai-platform.onrender.com/login"
            style="
                color:#2563eb;
                font-weight:bold;
                text-decoration:none;
            "
        >
            login to dashboard
        </a>
        for details.
        </p>

        <br>

        <p>
        Regards,<br>
        CJPS System
        </p>

        """
        response = resend.Emails.send({

            "from": "CJPS <onboarding@resend.dev>",

            "to": [to_email],

            "subject": subject,

            "html": html

        })

        print("✅ EMAIL SENT")
        print(response)

    except Exception as e:

        print("❌ EMAIL ERROR:", e)