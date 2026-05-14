import os

from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# Load .env
load_dotenv()


# DATABASE URL
DATABASE_URL = os.getenv("DATABASE_URL")


# PostgreSQL Engine
engine = create_engine(
    DATABASE_URL
)


# Session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base
Base = declarative_base()