from app.db.database import SessionLocal
from app.db.models import AttemptLog


def create_attempt_log(

    job_id,
    contractor_id,
    attempt_number,
    status,
    raw_notes,
    ai_rewritten_notes

):

    db = SessionLocal()

    attempt = AttemptLog(

        job_id=job_id,

        contractor_id=contractor_id,

        attempt_number=attempt_number,

        status=status,

        raw_notes=raw_notes,

        ai_rewritten_notes=ai_rewritten_notes

    )

    db.add(attempt)

    db.commit()

    db.refresh(attempt)

    db.close()

    return attempt