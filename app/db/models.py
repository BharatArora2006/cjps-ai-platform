from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text
)
from sqlalchemy.sql import func

from app.db.database import Base
from datetime import datetime

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)

    client_name = Column(String)
    client_email = Column(String)
    defendant_name = Column(String)
    address = Column(String)
    county = Column(String)
    instructions = Column(String)
    contractor_id = Column(Integer, nullable=True)
    status = Column(String, default="Pending")
    summary = Column(String)
    document_path = Column(String, nullable=True)
    created_at = Column(DateTime,default=datetime.utcnow)


class Admin(Base):

    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True)

    password = Column(String)

class Contractor(Base):
    __tablename__ = "contractors"

    id = Column(Integer, primary_key=True, index=True)
    contractor_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    county = Column(String, nullable=False)
    active_jobs = Column(Integer, default=0)
    status = Column(String, default="Active")
    password = Column(String)

class AttemptLog(Base):

    __tablename__ = "attempt_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    job_id = Column(
        Integer,
        ForeignKey("jobs.id")
    )

    contractor_id = Column(
        Integer,
        ForeignKey("contractors.id")
    )

    attempt_number = Column(
        Integer,
        default=1
    )

    status = Column(
        String,
        default="Attempted"
    )

    raw_notes = Column(
        Text
    )

    ai_rewritten_notes = Column(
        Text
    )

    photo_path = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

class AuditLog(Base):

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)

    action = Column(String)

    performed_by = Column(String)

    job_id = Column(Integer, nullable=True)

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )