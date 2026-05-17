import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=True)
    email = Column(String(120), unique=True, nullable=True)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, default=generate_uuid)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    job_postings = relationship("JobPosting", back_populates="session", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="session", cascade="all, delete-orphan")


class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    raw_text = Column(Text, nullable=True)
    source_type = Column(String, nullable=False)  # "text" or "screenshot"
    company_name = Column(String, nullable=True)
    position = Column(String, nullable=True)
    salary_range = Column(String, nullable=True)
    requirements = Column(Text, nullable=True)  # JSON array
    responsibilities = Column(Text, nullable=True)  # JSON array
    raw_json = Column(Text, nullable=True)  # Full AI extraction result
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="job_postings")
    resumes = relationship("Resume", back_populates="job_posting")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"), nullable=True)
    source_type = Column(String, nullable=False)  # "upload" or "generated"
    original_text = Column(Text, nullable=True)
    original_file_path = Column(String, nullable=True)
    optimized_text = Column(Text, nullable=True)
    optimized_html = Column(Text, nullable=True)
    matching_score = Column(Float, nullable=True)
    improvements = Column(Text, nullable=True)  # JSON array
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="resumes")
    job_posting = relationship("JobPosting", back_populates="resumes")
    skill_gaps = relationship("SkillGap", back_populates="resume", cascade="all, delete-orphan")


class SkillGap(Base):
    __tablename__ = "skill_gaps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    user_skills = Column(Text, nullable=True)  # JSON array
    required_skills = Column(Text, nullable=True)  # JSON array
    matching_skills = Column(Text, nullable=True)  # JSON array
    gap_skills = Column(Text, nullable=True)  # JSON array
    recommendations = Column(Text, nullable=True)  # JSON array
    overall_match_percentage = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    resume = relationship("Resume", back_populates="skill_gaps")
