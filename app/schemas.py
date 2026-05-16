from pydantic import BaseModel
from typing import Optional


class JobPostingInput(BaseModel):
    text: Optional[str] = None


class ResumeUploadInput(BaseModel):
    background: Optional[str] = None


class ResumeEditInput(BaseModel):
    optimized_text: str
    optimized_html: Optional[str] = None


class JobPostingResponse(BaseModel):
    id: int
    company_name: Optional[str] = None
    position: Optional[str] = None
    salary_range: Optional[str] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    raw_json: Optional[str] = None
    source_type: str

    class Config:
        from_attributes = True


class ResumeResponse(BaseModel):
    id: int
    job_posting_id: Optional[int] = None
    source_type: str
    original_text: Optional[str] = None
    optimized_text: Optional[str] = None
    optimized_html: Optional[str] = None
    matching_score: Optional[float] = None
    improvements: Optional[str] = None

    class Config:
        from_attributes = True


class SkillGapResponse(BaseModel):
    id: int
    resume_id: int
    matching_skills: Optional[str] = None
    gap_skills: Optional[str] = None
    recommendations: Optional[str] = None
    overall_match_percentage: Optional[float] = None

    class Config:
        from_attributes = True
