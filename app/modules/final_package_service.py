import resend
import os

from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv(
    "RESEND_API_KEY"
)


def send_final_package(

    client_email,
    client_name,
    affidavit_url,
    invoice_url,
    job_id,
    payment_link

):

    subject = (
    f"Final Service Documents - "
    f"Job #{job_id}"
)

    html = f"""
    <h2>Service Completed</h2>

    <p>Hello {client_name},</p>

    <p>
    The requested process service has been completed.
    Please find your final documents below.
    </p>

    <p>
    <a href="{affidavit_url}">
    Download Affidavit
    </a>
    </p>

    <p>
    <a href="{invoice_url}">
    Download Invoice
    </a>
    </p>

    <br/>

    <p>
    Please complete payment using the secure link below:
    </p>

    <p>
    <a
        href="{payment_link}"

        style="
            background:#2563eb;
            color:white;
            padding:14px 22px;
            border-radius:10px;
            text-decoration:none;
            font-weight:bold;
            display:inline-block;
        "
    >
        💳 Pay Invoice
    </a>
    </p>

    <br/>

    <p>
    Thank you for your business.
    </p>

    """
    print(subject)
    resend.Emails.send({

        "from":
        "CJPS Legal Ops <onboarding@resend.dev>",

        "to":
        client_email,

        "subject":
        subject,

        "html":
        html

    })

    print(
        "FINAL PACKAGE SENT"
    )