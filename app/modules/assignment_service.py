from app.db.database import SessionLocal
from app.db.models import Contractor


def assign_contractor(county: str):

    print("🔥 COUNTY RECEIVED:", county)

    db = SessionLocal()

    try:

        contractors = db.query(Contractor).filter(
            Contractor.county.ilike(f"%{county}%"),
            Contractor.status == "Active"
        ).all()

        print("🔥 MATCHING CONTRACTORS:", contractors)

        if not contractors:
            print("❌ NO CONTRACTORS FOUND")
            return None

        selected = min(contractors, key=lambda c: c.active_jobs)

        print("✅ SELECTED:", selected.contractor_name)

        selected.active_jobs += 1

        db.commit()

        return selected.id

    finally:
        db.close()