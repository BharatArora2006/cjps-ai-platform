from app.db.database import SessionLocal
from app.db.models import Job, Contractor

from app.modules.assignment_service import assign_contractor
from app.modules.notification_service import send_assignment_email


def create_job(
        data, 
        document_path=None,
         summary=None
        ):

    db = SessionLocal()

    # Assign contractor
    contractor_id = assign_contractor(data["county"])

    print("🔥 CONTRACTOR ID:", contractor_id)

    # Fetch contractor object
    contractor = None

    if contractor_id:

        contractor = db.query(Contractor).filter(
            Contractor.id == contractor_id
        ).first()

    # Create job
    job = Job(
        client_name=data["client_name"],
        defendant_name=data["defendant_name"],
        address=data["address"],
        county=data["county"],
        instructions=data["instructions"],
        contractor_id=contractor_id,
        document_path=document_path,
        summary=summary,
        status="Assigned" if contractor_id else "Pending"
    )

    db.add(job)

    db.commit()

    db.refresh(job)

    # SEND EMAIL
    if contractor:

        print("🔥 EMAIL FUNCTION CALLED")

        send_assignment_email(
            contractor.email,
            contractor.contractor_name,
            data
        )

    db.close()

    return job