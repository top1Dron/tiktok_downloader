"""Database models and session management."""

from sqlalchemy import create_engine, Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL - must be set in environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is required. "
        "Set it in .env file or environment. "
        "Example: postgresql://user:password@localhost:5432/dbname"
    )

# Heroku uses postgres:// but SQLAlchemy requires postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class DownloadTask(Base):
    """Download task model."""

    __tablename__ = "download_tasks"

    task_id = Column(String, primary_key=True, index=True)
    celery_task_id = Column(String, unique=True, index=True)
    url = Column(Text, nullable=False)
    status = Column(
        String, default="pending"
    )  # pending, downloading, completed, failed
    file_path = Column(Text, nullable=True)
    file_name = Column(String, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
