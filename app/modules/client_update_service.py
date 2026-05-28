import os
import resend


resend.api_key = os.getenv(
    "RESEND_API_KEY"
)


def send_client_attempt_update(

    client_email,
    job_id,
    status,
    ai_notes,
    attempt_number,
    photo_url=None
    

):

    html = f"""

    <h2>Service Attempt Update</h2>

    <p>
        <strong>Job ID:</strong>
        {job_id}
    </p>

    <p>
        <strong>Attempt No.:</strong>
        {attempt_number}
    </p>


    <p>
        <strong>Status:</strong>
        {status}
    </p>

    <p>
        <strong>Professional Notes:</strong><br>
        {ai_notes}
    </p>

    """

    if photo_url:

        html += f"""

        <p>
            <strong>Photo Evidence:</strong>
        </p>

        <img
            src="{photo_url}"
            width="300"
            style="border-radius:12px;"
        >

        """
    print("CALLING RESEND")
    
    resend.Emails.send({

        "from": "CJPS <onboarding@resend.dev>",

        "to": [client_email],

        "subject": (
            f"Process Service Attempt #{attempt_number} "
            f"- Job #{job_id}"
            ),

        "html": html

    })