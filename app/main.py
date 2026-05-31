print("✅ RUNNING MAIN.PY ✅")

from fastapi import FastAPI, Request, Depends,BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi import UploadFile, File, Form
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import SessionLocal, engine
from app.db.models import Job, Contractor, Admin, Base, AuditLog, AttemptLog

from app.modules.email_reader import read_email
from app.modules.pdf_parser import extract_text_from_pdf
from app.modules.ai_parser import extract_job_data
from app.modules.job_service import create_job
from app.modules.summary_service import generate_case_summary
from app.modules.storage_service import upload_file_to_supabase, upload_attempt_photo_to_supabase
from app.modules.attempt_service import create_attempt_log
from app.modules.ai_note_service import rewrite_attempt_note
from app.modules.client_update_service import send_client_attempt_update
from app.modules.affidavit_service import generate_affidavit_pdf
from app.modules.invoice_service import generate_invoice_pdf
from app.modules.final_package_service import send_final_package
from app.modules.payment_service import create_payment_link
from app.modules.security import hash_password,verify_password

from starlette.middleware.sessions import SessionMiddleware
import os
from datetime import datetime, timedelta
import time

# ✅ Create uploads folder if missing
os.makedirs("uploads", exist_ok=True)

# ✅ Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
    )

os.makedirs(
    "generated_affidavits",
    exist_ok=True
)
app.mount(
    "/generated_affidavits",
    StaticFiles(directory="generated_affidavits"),
    name="generated_affidavits"
)

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ SESSION MIDDLEWARE
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY")
)

# ✅ Templates
templates = Jinja2Templates(directory="app/templates")


# ✅ DB Dependency

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_admin(request: Request):

    admin_id = request.session.get("admin_id")

    if not admin_id:

        return False

    return True

def require_contractor(request: Request):

    contractor_id = request.session.get("contractor_id")

    if not contractor_id:

        return False

    return contractor_id

# ✅ HEALTH
@app.get("/health")
def health():
    return {"status": "ok"}


# ✅ PROCESS EMAIL
@app.post("/process-email/")
def process_email(db: Session = Depends(get_db)):

    email_text, attachments = read_email("sample.eml")

    full_pdf_text = ""

    for file in attachments:
        full_pdf_text += extract_text_from_pdf(file)

    data = extract_job_data(email_text, full_pdf_text)
    
    job = create_job(data)

    return {
        "message": "Job created",
        "job_id": job.id,
        "data": data
    }


# ✅ DASHBOARD
@app.get("/dashboard")
def dashboard(
    request: Request,
    search: str = "",
    status: str = "",
    county: str = "",
    contractor_id: str = ""
):

    if not require_admin(request):

        return RedirectResponse(
            url="/admin-login",
            status_code=303
        )

    # ✅ CHECK ADMIN LOGIN
    admin_id = request.session.get("admin_id")

    if not admin_id:

        return RedirectResponse(
            url="/admin-login",
            status_code=303
        )

    print("🔥 DASHBOARD ROUTE HIT")

    db = SessionLocal()

    invoice_approved = request.query_params.get(
        "invoice_approved"
    )

    try:

        # ✅ JOB QUERY
        query = db.query(Job)

        

        # ✅ SEARCH
        if search:

            query = query.filter(
                Job.client_name.ilike(f"%{search}%")
                |
                Job.defendant_name.ilike(f"%{search}%")
                |
                Job.county.ilike(f"%{search}%")
            )

        # ✅ STATUS FILTER
        if status:

            query = query.filter(
                Job.status == status
            )

        # ✅ COUNTY FILTER
        if county:

            query = query.filter(
                Job.county.ilike(f"%{county}%")
            )

        # ✅ CONTRACTOR FILTER
        if contractor_id:

            query = query.filter(
                Job.contractor_id == int(contractor_id)
            )

        # ✅ FETCH FILTERED JOBS
        jobs_db = query.all()

        # ✅ FETCH ALL CONTRACTORS
        contractors_db = db.query(Contractor).all()

        contractors = [
            {
                "id": c.id,
                "name": c.contractor_name
            }
            for c in contractors_db
        ]

        jobs = []

        for j in jobs_db:
            attempts = db.query(AttemptLog).filter(
                AttemptLog.job_id == j.id
            ).all()
            contractor_name = "Not Assigned"

            print(
                "JOB CONTRACTOR ID:",
                j.contractor_id
            )

            if j.contractor_id:

                contractor = db.query(
                    Contractor
                ).filter(
                    Contractor.id == j.contractor_id
                ).first()

                print(
                    "FOUND CONTRACTOR:",
                    contractor
                )

                if contractor:

                    contractor_name = (
                        contractor.contractor_name
                    )

            # ✅ SLA OVERDUE CHECK
            is_overdue = False

            if j.created_at:

                age = (
                    datetime.utcnow()
                    - j.created_at
                )

                if (
                    age > timedelta(days=3)
                    and j.status not in [
                        "Completed",
                        "Approved"
                    ]
                ):

                    is_overdue = True

            jobs.append({

                "id": j.id,

                "client_name": j.client_name,

                "defendant_name": j.defendant_name,

                "address": j.address,

                "county": j.county,

                "status": j.status,

                "invoice_status": j.invoice_status,

                "invoice_approved": j.invoice_approved,

                "attempts": attempts,

                "contractor_name": contractor_name,

                "document_path": j.document_path,

                "affidavit_path": j.affidavit_path,

                "invoice_path": j.invoice_path,

                "is_overdue": is_overdue,

                "created_at": (
                    j.created_at.strftime("%Y-%m-%d")
                    if j.created_at
                    else "N/A"
                ),

                "summary": j.summary

            })

    except Exception as e:

        print(
            "DASHBOARD ERROR:",
            str(e)
        )

        return templates.TemplateResponse(
            name="dashboard.html",
            request=request,
            context={
                "error": (
                    "Something went wrong "
                    "while loading dashboard."
                ),
                "jobs": []
            }
        )

    finally:

        db.close()

    success = request.query_params.get(
        "success"
    )

    return templates.TemplateResponse(
        name="dashboard.html",
        request=request,
        context={

            "jobs": jobs,

            "contractors": contractors,

            "success": success,

            "search": search,

            "selected_status": status,

            "selected_county": county,

            "selected_contractor": contractor_id,

            "invoice_approved": invoice_approved

        }
    )


# ✅ APPROVE JOB
@app.post("/jobs/{job_id}/approve")
def approve_job(
    request: Request,
    job_id: int
):

    if not require_admin(request):

        return RedirectResponse(
            url="/admin-login",
            status_code=303
        )

    db = SessionLocal()

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if job:

        job.status = "Approved"

        db.commit()

    db.close()

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )

# ✅ REJECT JOB
@app.post("/jobs/{job_id}/reject")
def reject_job(request: Request, job_id: int):

    db = SessionLocal()

    job = db.query(Job).filter(Job.id == job_id).first()

    if job:
        job.status = "Rejected"
        db.commit()

    db.close()

    return RedirectResponse(url="/dashboard", status_code=303)

@app.post("/jobs/{job_id}/reassign")
def reassign_job(
    request: Request,
    job_id: int,
    contractor_id: int = Form(...)
):

    # ✅ ADMIN SECURITY CHECK
    if not require_admin(request):

        return RedirectResponse(
            url="/admin-login",
            status_code=303
        )

    print("🔥 REASSIGN HIT")
    print("JOB ID:", job_id)
    print("NEW CONTRACTOR ID:", contractor_id)

    db = SessionLocal()

    try:

        # Find job
        job = db.query(Job).filter(
            Job.id == job_id
        ).first()

        if not job:

            print("❌ JOB NOT FOUND")

            return RedirectResponse(
                url="/dashboard",
                status_code=303
            )

        print("✅ JOB FOUND")

        # OLD contractor
        old_contractor = None

        if job.contractor_id:

            old_contractor = db.query(Contractor).filter(
                Contractor.id == job.contractor_id
            ).first()

        # NEW contractor
        new_contractor = db.query(Contractor).filter(
            Contractor.id == contractor_id
        ).first()

        print("OLD CONTRACTOR:", old_contractor)
        print("NEW CONTRACTOR:", new_contractor)

        # Reduce old workload
        if old_contractor and old_contractor.active_jobs > 0:

            old_contractor.active_jobs -= 1

        # Increase new workload
        if new_contractor:

            new_contractor.active_jobs += 1

        # Update job
        job.contractor_id = contractor_id

        job.status = "Reassigned"

        db.commit()

        print("✅ REASSIGN SUCCESS")

    finally:

        db.close()

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )

# ✅ SHOW UPLOAD PAGE
@app.get("/upload")
def upload_page(request: Request):

    print("🔥 UPLOAD PAGE HIT")

    return templates.TemplateResponse(
        name="upload.html",
        request=request,
        context={
            "request": request
        }
    )


# ✅ HANDLE FILE UPLOAD

@app.post("/upload")
async def upload_files(
    request: Request,
    background_tasks: BackgroundTasks,
    email_text: str = Form(...),
    files: list[UploadFile] = File(...)
):

    start_time = time.time()
    full_pdf_text = ""

    saved_file_path = None

    print("FILES RECEIVED:", len(files))

    for file in files:

        print("PROCESSING:", file.filename)

        # RESET FILE POINTER
        file.file.seek(0)

        # READ FILE ONLY ONCE
        file_bytes = file.file.read()

        print("RAW BYTES:", len(file_bytes))

        safe_filename = file.filename.lower()

        # CREATE TEMP FOLDER
        os.makedirs("temp", exist_ok=True)

        file_path = f"temp/{safe_filename}"

        # SAVE TEMP FILE
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        print(
            "LOCAL FILE SIZE:",
            os.path.getsize(file_path)
        )

        # EXTRACT PDF TEXT
        print("FILE PATH:", file_path)
        print("FILE SIZE:", os.path.getsize(file_path))
        extracted_text = extract_text_from_pdf(
            file_path
        )

        full_pdf_text += extracted_text

        # UPLOAD TO SUPABASE
        public_url = upload_file_to_supabase(
            file_path,
            safe_filename
        )

        print(
            "SUPABASE FILE URL:",
            public_url
        )

        # SAVE FIRST FILE URL
        if not saved_file_path:
            saved_file_path = public_url

    # AI EXTRACTION
    data = extract_job_data(
        email_text,
        full_pdf_text
    )

    processing_time = round(
        time.time() - start_time,
        2
    )

    # AI SUMMARY
    summary = generate_case_summary(data)
    
    # SAVE JOB
    create_job(
        data,
        document_path=saved_file_path,
        summary=summary,
        processing_time=processing_time
    )

    return RedirectResponse(
        url="/dashboard?success=1",
        status_code=303
    )

@app.get("/contractor/{contractor_id}/jobs")
def contractor_jobs(
    contractor_id: int,
    request: Request
):
    print("SESSION:", request.session)
    # ✅ SESSION CHECK
    logged_in_contractor = request.session.get("contractor_id")

    admin_id = request.session.get("admin_id")

    # ✅ ALLOW ADMIN ACCESS
    if admin_id:

        pass

    # ✅ ALLOW ONLY OWN CONTRACTOR PAGE
    elif logged_in_contractor != contractor_id:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    db = SessionLocal()

    jobs_db = db.query(Job).filter(
        Job.contractor_id == contractor_id
    ).all()

    contractor = db.query(Contractor).filter(
        Contractor.id == contractor_id
    ).first()

    attempts_db = db.query(
        AttemptLog
    ).all()

    attempts = []

    for a in attempts_db:

        attempts.append({

            "id": a.id,

            "job_id": a.job_id,

            "attempt_number": a.attempt_number,

            "status": a.status,

            "raw_notes": a.raw_notes,

            "ai_rewritten_notes": a.ai_rewritten_notes,

            "photo_path": a.photo_path,

            "created_at": (
                a.created_at.strftime("%Y-%m-%d %H:%M")
                if a.created_at
                else ""
            )

        })

    jobs = []

    

    for j in jobs_db:
        attempts = db.query(AttemptLog).filter(
            AttemptLog.job_id == j.id
        ).all()
        jobs.append({

            "id": j.id,

            "attempts": attempts,

            "client_name": j.client_name,

            "defendant_name": j.defendant_name,

            "address": j.address,

            "status": j.status,

            "invoice_status": j.invoice_status,

            "invoice_approved": j.invoice_approved,

            "document_path": j.document_path,

            "affidavit_path": j.affidavit_path

        })
    db.close()

    for job in jobs:
        print("JOB:", job["id"])
        print("AFFIDAVIT:", job.get("affidavit_path"))

    return templates.TemplateResponse(
        name="contractor_jobs.html",
        request=request,
        context={
            "jobs": jobs,
            "contractor": contractor,
            "attempts": attempts
        }
    )

# ✅ HANDLE UPDATE
@app.post("/jobs/{job_id}/update-status")
def update_job_status(
    job_id: int,
    status: str = Form(...)
    ):

    db = SessionLocal()

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if job:

       
        print("OLD STATUS:", job.status)

        job.status = status

        print("NEW STATUS:", status)

        db.commit()

        db.refresh(job)

        print("UPDATED STATUS:", job.status)

    # AUTO AFFIDAVIT
    if status == "Completed":

        contractor = db.query(
            Contractor
        ).filter(
            Contractor.id == job.contractor_id
        ).first()

        attempts = db.query(
            AttemptLog
        ).filter(
            AttemptLog.job_id == job.id
        ).order_by(
            AttemptLog.attempt_number.asc()
        ).all()

        if contractor and attempts:

            affidavit_path = (
                generate_affidavit_pdf(
                    job,
                    contractor,
                    attempts
                )
            )

            job.affidavit_path = (
                affidavit_path
            )
        
            print("AFFIDAVIT SAVED")

            invoice_url = (
                generate_invoice_pdf(
                    job,
                    contractor
                )
            )

            job.invoice_path = (
                invoice_url
            )
            print("INVOICE SAVED")

        # ✅ CREATE AUDIT LOG
        log = AuditLog(
            action=f"Status changed to {status}",
            performed_by="Contractor",
            job_id=job.id
        )

        db.add(log)
        
        contractor.active_jobs = max(
            0,
            contractor.active_jobs - 1
        )

        db.commit()
        # print("UPDATED STATUS:", job.status)

        contractor_id = job.contractor_id

    else:
        contractor_id = 1

    db.close()

    return RedirectResponse(
        url="/my-jobs",
        status_code=303
    )

@app.get("/login")
def login_page(request: Request):
    print(type(templates))
    return templates.TemplateResponse(
        name="login.html",
        request=request,
        context={}
    )

@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):

    db = SessionLocal()

    contractor = db.query(Contractor).filter(
        Contractor.email == email
    ).first()
    print("INPUT PASSWORD:", password)

    if contractor:
        print("DB PASSWORD:", contractor.password)

    if contractor and verify_password(
        password,
        contractor.password
    ):

        request.session["contractor_id"] = contractor.id

        db.close()

        return RedirectResponse(
            url="/my-jobs",
            status_code=303
        )

    db.close()

    return templates.TemplateResponse(
        name="login.html",
        request=request,
        context={
            "error": "Invalid credentials"
        }
    )

@app.get("/my-jobs")
def my_jobs(request: Request):

    contractor_id = request.session.get("contractor_id")

    if not contractor_id:
        return RedirectResponse("/login")

    return RedirectResponse(
        url=f"/contractor/{contractor_id}/jobs",
        status_code=303
    )

@app.get("/admin-login")
def admin_login_page(request: Request):

    return templates.TemplateResponse(
        name="admin_login.html",
        request=request,
        context={}
    )

@app.post("/admin-login")
def admin_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):

    db = SessionLocal()

    admin = db.query(Admin).filter(
        Admin.email == email
    ).first()

    db.close()

    if admin and verify_password(
        password,
        admin.password
    ):

        request.session.clear()

        request.session["admin_id"] = admin.id

        return RedirectResponse(
            url="/dashboard",
            status_code=303
        )

    return HTMLResponse(
        "Invalid admin credentials"
    )


@app.get("/audit-logs")
def audit_logs(request: Request):

    db = SessionLocal()

    logs = db.query(AuditLog).order_by(
        AuditLog.timestamp.desc()
    ).all()

    db.close()

    return templates.TemplateResponse(
        name="audit_logs.html",
        request=request,
        context={
            "logs": logs
        }
    )

# ✅ LOGOUT
@app.get("/logout")
def logout(request: Request):

    request.session.clear()

    return RedirectResponse(
        url="/login",
        status_code=303
    )


@app.get("/analytics")
def analytics_dashboard(
    request: Request
):

    # ✅ ADMIN SECURITY
    if not require_admin(request):

        return RedirectResponse(
            url="/admin-login",
            status_code=303
        )

    db = SessionLocal()

    # TOTALS
    total_jobs = db.query(Job).count()

    approved_jobs = db.query(Job).filter(
        Job.status == "Approved"
    ).count()

    rejected_jobs = db.query(Job).filter(
        Job.status == "Rejected"
    ).count()

    completed_jobs = db.query(Job).filter(
        Job.status == "Completed"
    ).count()

    assigned_jobs = db.query(Job).filter(
        Job.status == "Assigned"
    ).count()

    # COUNTY ANALYTICS
    jobs_db = db.query(Job).all()

    county_data = {}

    for job in jobs_db:

        county = job.county or "Unknown"

        county_data[county] = county_data.get(
            county,
            0
        ) + 1

    # CONTRACTOR ANALYTICS
    contractors_db = db.query(Contractor).all()

    contractor_labels = []

    contractor_jobs = []

    for contractor in contractors_db:

        contractor_labels.append(
            contractor.contractor_name
        )

        contractor_jobs.append(
            contractor.active_jobs or 0
        )

    ai_processed_jobs = db.query(Job).filter(
        Job.ai_processed == True
    ).count()

    manual_review_jobs = db.query(Job).filter(
        Job.manual_review_required == True
    ).count()

    avg_ai_time_query = db.query(
        func.avg(Job.ai_processing_time)
    ).scalar()

    avg_ai_time = round(
        avg_ai_time_query or 0,
        2
    )

    if total_jobs > 0:

        ai_success_rate = round(
            (ai_processed_jobs / total_jobs) * 100,
            2
        )

    else:

        ai_success_rate = 0

    db.close()

    return templates.TemplateResponse(
        name="analytics.html",
        request=request,
        context={

            "total_jobs": total_jobs,
            "approved_jobs": approved_jobs,
            "rejected_jobs": rejected_jobs,
            "completed_jobs": completed_jobs,
            "assigned_jobs": assigned_jobs,

            "county_labels": list(county_data.keys()),
            "county_values": list(county_data.values()),

            "contractor_labels": contractor_labels,
            "contractor_jobs": contractor_jobs,
           
            "ai_processed_jobs": ai_processed_jobs,
            "manual_review_jobs": manual_review_jobs,
            "avg_ai_time": avg_ai_time,
            "ai_success_rate": ai_success_rate
        }
    )

@app.post("/log-attempt/{job_id}")
async def log_attempt(

    job_id: int,

    request: Request,

    status: str = Form(...),

    raw_notes: str = Form(...),

    photo: UploadFile = File(None)
   

):

    contractor_id = request.session.get(
        "contractor_id"
    )

    print(
        "SESSION CONTRACTOR ID:",
        contractor_id
    )

    if not contractor_id:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    db = SessionLocal()

    existing_attempts = db.query(
        AttemptLog
    ).filter(
        AttemptLog.job_id == job_id
    ).count()

    attempt_number = existing_attempts + 1

    # AI NOTE REWRITE
    ai_note = rewrite_attempt_note(
        raw_notes
    )

    print("AI NOTE:", ai_note)

    # PHOTO UPLOAD
    photo_path = None

    if photo and photo.filename:

        os.makedirs(
            "temp",
            exist_ok=True
        )

        temp_path = (
            f"temp/{photo.filename}"
        )

        contents = await photo.read()

        with open(temp_path, "wb") as f:
            f.write(contents)

        photo_path = (
            upload_attempt_photo_to_supabase(
                temp_path,
                photo.filename
            )
        )

        print(
            "SUPABASE PHOTO URL:",
            photo_path
        )

    # SAVE ATTEMPT
    create_attempt_log(

        job_id=job_id,

        contractor_id=contractor_id,


        attempt_number=attempt_number,

        status=status,

        raw_notes=raw_notes,

        ai_rewritten_notes=ai_note,

        photo_path=photo_path

    )
    db.commit()

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if job and job.client_email:
        print("SENDING ATTEMPT EMAIL")
        print("ATTEMPT NUMBER:", attempt_number)

        send_client_attempt_update(

            client_email=job.client_email,

            job_id=job.id,

            attempt_number=attempt_number,

            status=status,

            ai_notes=ai_note,

            photo_url=photo_path

        )
        print("ATTEMPT EMAIL SENT")
    db.commit()
    db.close()

    return RedirectResponse(

        url=f"/contractor/{contractor_id}/jobs?attempt_success=1",

        status_code=303

    )

@app.post("/jobs/{job_id}/send-final-package")
def send_final_package_route(
    job_id: int
):

    db = SessionLocal()

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if job:

        send_final_package(

            client_email=job.client_email,

            client_name=job.client_name,

            affidavit_url=job.affidavit_path,

            invoice_url=job.invoice_path,

            job_id=job.id,

            payment_link=job.payment_link

        )

        job.invoice_status = "Sent"

        db.commit()

        send_final_package(

            client_email=job.client_email,

            client_name=job.client_name,

            affidavit_url=job.affidavit_path,

            invoice_url=job.invoice_path,

            job_id=job.id,

            payment_link=job.payment_link

        )

        print("FINAL PACKAGE SENT")

        job.invoice_status = "Sent"

        db.commit()

    db.close()

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )
# AFFIDAVIT APPROVAL
@app.post("/jobs/{job_id}/approve-invoice")
def approve_invoice(
    job_id: int
):

    db = SessionLocal()

    job = db.query(Job).filter(
        Job.id == job_id
    ).first()

    if job:

        job.invoice_approved = True
        job.invoice_status = "Approved"
        job.payment_link = (create_payment_link(job))
        print("BEFORE COMMIT:")
        print(job.invoice_approved)
        print(job.invoice_status)
        db.commit()
        print("AFTER COMMIT:")
        print(job.invoice_approved)
        print(job.invoice_status)
        
        send_final_package(

            client_email=job.client_email,

            client_name=job.client_name,

            affidavit_url=job.affidavit_path,

            invoice_url=job.invoice_path,

            job_id=job.id,

            payment_link=job.payment_link

        )

        print("FINAL PACKAGE SENT")

    db.close()

    return RedirectResponse(
        url="/dashboard?invoice_approved=1",
        status_code=303
    )


# DUMMY SETUP
@app.get("/seed-admin")
def seed_admin():

    db = SessionLocal()

    existing = db.query(Admin).filter(
        Admin.email == "admin@test.com"
    ).first()

    if existing:

        db.close()

        return {
            "message": "Admin already exists"
        }

    admin = Admin(
        email="admin@test.com",
        password=hash_password("admin123")
    )

    db.add(admin)

    db.commit()

    db.close()

    return {
        "message": "Admin created"
    }


# ✅ SEED CONTRACTORS
@app.get("/seed-contractors")
def seed_contractors():

    db = SessionLocal()

    sample_contractors = [

        {
            "contractor_name": "Mike Services",
            "email": "lwilks752@gmail.com",
            "phone": "1111111111",
            "county": "Essex County",
            "password": "test123"
        },

        {
            "contractor_name": "John Legal Services",
            "email": "lwilks752@gmail.com",
            "phone": "2222222222",
            "county": "Hudson County",
            "password": "test123"
        },

        {
            "contractor_name": "NJ Process Servers",
            "email": "lwilks752@gmail.com",
            "phone": "3333333333",
            "county": "Essex County",
            "password": "test123"
        },
        {
            "contractor_name": "BA Process Servers",
            "email": "lwilks752@gmail.com",
            "phone": "123456789",
            "county": "NOIDA County",
            "password": "test123"
        }
    ]

    for c in sample_contractors:

        contractor = Contractor(
            contractor_name=c["contractor_name"],
            email=c["email"],
            phone=c["phone"],
            county=c["county"],
            password=hash_password(c["password"])
        )

        db.add(contractor)

    db.commit()

    db.close()

    return {"message": "Sample contractors added"}
