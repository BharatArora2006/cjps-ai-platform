from app.db.database import SessionLocal
from app.db.models import Job, Contractor,AttemptLog

from app.modules.assignment_service import assign_contractor
from app.modules.notification_service import send_assignment_email


def create_job(
        data, 
        processing_time,
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
        client_email=data.get("client_email"),
        defendant_name=data["defendant_name"],
        address=data["address"],
        county=data["county"],
        instructions=data["instructions"],
        contractor_id=contractor_id,
        document_path=document_path,
        summary=summary,
        status="Assigned" if contractor_id else "Pending",
        ai_processed=True,
        ai_processing_time=processing_time,
        manual_review_required=False
    )

    db.add(job)

    db.commit()

    db.refresh(job)

    # SEND EMAIL
    if contractor:

        print("🔥 EMAIL FUNCTION CALLED")

        try:
            send_assignment_email(
                contractor.email,
                contractor.contractor_name,
                data
            )

        except Exception as e:

            print("EMAIL ERROR:", e)

    db.close()

    return job