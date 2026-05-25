import os
from datetime import datetime
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)

from reportlab.lib.pagesizes import (
    letter
)

from app.modules.storage_service import (
    upload_affidavit_to_supabase
)


def generate_invoice_pdf(

    job,
    contractor

):

    os.makedirs(
        "generated_invoices",
        exist_ok=True
    )

    filename = (
        f"generated_invoices/invoice_job_{job.id}.pdf"
    )

    year = datetime.utcnow().year

    invoice_number = (
        f"CJPS-{year}-{job.id:05d}"
    )

    job.invoice_number = invoice_number

    doc = SimpleDocTemplate(
        filename,
        pagesize=letter
    )

    styles = getSampleStyleSheet()

    elements = []

    title = Paragraph(
        "<b>CIVIL PROCESS SERVICE INVOICE</b>",
        styles["Title"]
    )

    elements.append(title)

    elements.append(
        Spacer(1, 20)
    )

    invoice_text = f"""
    
<b>Invoice Number:</b>
{job.invoice_number}

<br/><br/>

<b>Invoice Date:</b>
{job.created_at.strftime("%B %d, %Y")}

<br/><br/>

<b>Invoice For:</b>
{job.client_name}

<br/><br/>

<b>Defendant:</b>
{job.defendant_name}

<br/><br/>

<b>Service Type:</b>
Process Serving

<br/><br/>

<b>Service Address:</b>
{job.address}

<br/><br/>

<b>Assigned Process Server:</b>
{contractor.contractor_name}

<br/><br/>

<b>Total Amount:</b>
${job.invoice_amount:.2f}

<br/><br/>

Thank you for your business.
"""

    body = Paragraph(
        invoice_text,
        styles["BodyText"]
    )

    elements.append(body)

    doc.build(elements)

    invoice_url = (
        upload_affidavit_to_supabase(
            filename,
            os.path.basename(filename)
        )
    )

    return invoice_url