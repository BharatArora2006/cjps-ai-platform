import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from app.modules.storage_service import upload_affidavit_to_supabase



def generate_affidavit_pdf(

    job,
    contractor,
    latest_attempt

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

    title = Paragraph(
        "<b>AFFIDAVIT OF SERVICE</b>",
        styles["Title"]
    )

    elements.append(title)

    elements.append(
        Spacer(1, 20)
    )

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

    <b>Status:</b> {latest_attempt.status}

    <br/><br/>

    <b>Attempt Notes:</b>
    {latest_attempt.ai_rewritten_notes}

    <br/><br/>

    I certify the above information is true
    and accurate to the best of my knowledge.
    """

    body = Paragraph(
        affidavit_text,
        styles["BodyText"]
    )

    elements.append(body)

    elements.append(
        Spacer(1, 50)
    )

    signature = Paragraph(
        f"""
        _______________________<br/>
        {contractor.contractor_name}<br/>
        Process Server
        """,
        styles["BodyText"]
    )

    elements.append(signature)

    doc.build(elements)

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