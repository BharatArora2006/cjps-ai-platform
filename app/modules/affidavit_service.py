import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from app.modules.storage_service import upload_affidavit_to_supabase

def generate_affidavit_pdf(

    job,
    contractor,
    attempts

):

    os.makedirs(
        "generated_affidavits",
        exist_ok=True
    )

    filename = (
        f"generated_affidavits/affidavit_job_{job.id}.pdf"
    )

    doc = SimpleDocTemplate(
        filename,
        pagesize=letter
    )

    styles = getSampleStyleSheet()

    elements = []

    # TITLE
    title = Paragraph(
        "<b>AFFIDAVIT OF SERVICE</b>",
        styles["Title"]
    )

    elements.append(title)

    elements.append(
        Spacer(1, 20)
    )

    # CASE DETAILS
    affidavit_text = f"""
    I, {contractor.contractor_name},
    certify that service was attempted/completed
    for the following matter:

    <br/><br/>

    <b>Client:</b> {job.client_name}

    <br/><br/>

    <b>Defendant:</b> {job.defendant_name}

    <br/><br/>

    <b>Address:</b> {job.address}

    <br/><br/>

    I certify the below service attempt history
    is accurate to the best of my knowledge.
    """

    body = Paragraph(
        affidavit_text,
        styles["BodyText"]
    )

    elements.append(body)

    elements.append(
        Spacer(1, 20)
    )

    # ATTEMPT HISTORY
    elements.append(
        Paragraph(
            "<b>Service Attempt History</b>",
            styles["Heading2"]
        )
    )

    elements.append(
        Spacer(1, 10)
    )

    for attempt in attempts:

        attempt_text = f"""
        <b>Attempt #{attempt.attempt_number}</b>

        <br/><br/>

        <b>Status:</b> {attempt.status}

        <br/><br/>

        <b>Notes:</b>
        {attempt.ai_rewritten_notes}
        """

        attempt_paragraph = Paragraph(
            attempt_text,
            styles["BodyText"]
        )

        elements.append(
            attempt_paragraph
        )

        elements.append(
            Spacer(1, 15)
        )

    # SIGNATURE
    signature = Paragraph(
        f"""
        <br/><br/><br/>

        _______________________<br/>

        {contractor.contractor_name}<br/>

        Process Server
        """,
        styles["BodyText"]
    )

    elements.append(signature)

    # BUILD PDF
    doc.build(elements)

    # UPLOAD TO SUPABASE
    supabase_url = (
        upload_affidavit_to_supabase(
            filename,
            os.path.basename(filename)
        )
    )

    print(
        "AFFIDAVIT UPLOADED:",
        supabase_url
    )

    return supabase_url