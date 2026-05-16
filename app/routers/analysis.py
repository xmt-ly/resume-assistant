import json
import logging
import re

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Resume, JobPosting, SkillGap
from app.services.ai_service import AIService
from app.services.resume_optimizer import ResumeOptimizer

router = APIRouter(tags=["analysis"])
logger = logging.getLogger(__name__)

ai_service = AIService()
resume_optimizer = ResumeOptimizer(ai_service)


@router.post("/analysis/{resume_id}")
async def create_analysis(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        return JSONResponse(status_code=404, content={"error": "简历不存在"})

    existing = db.query(SkillGap).filter(SkillGap.resume_id == resume_id).first()
    if existing:
        db.delete(existing)
        db.commit()

    job = None
    required_skills = []
    job_data = {}
    if resume.job_posting_id:
        job = db.query(JobPosting).filter(JobPosting.id == resume.job_posting_id).first()
        if job:
            required_skills = json.loads(job.requirements) if job.requirements else []
            job_data = {
                "position": job.position,
                "company_name": job.company_name,
                "salary_range": job.salary_range,
                "requirements_skills": required_skills,
            }

    resume_text = resume.original_text or resume.optimized_text or ""

    try:
        result = resume_optimizer.analyze_gaps(resume_text, job_data)
    except Exception as e:
        logger.warning(f"AI skill gap analysis failed, using fallback: {e}")
        result = {
            "matching_skills": [],
            "gap_skills": [{"name": s, "required_level": "需要"} for s in required_skills] if required_skills else [],
            "partial_skills": [],
            "recommendations": [{"skill": s, "priority": "medium", "reason": "职位描述中提及的技能", "resources": ["查阅相关文档和教程"]} for s in required_skills] if required_skills else [],
            "overall_match_percentage": 50,
        }

    overall_match = result.get("overall_match_percentage", 50)
    skill_gap = SkillGap(
        resume_id=resume_id,
        user_skills=json.dumps([], ensure_ascii=False),
        required_skills=json.dumps(required_skills, ensure_ascii=False),
        matching_skills=json.dumps(result.get("matching_skills", []), ensure_ascii=False),
        gap_skills=json.dumps(result.get("gap_skills", []), ensure_ascii=False),
        recommendations=json.dumps(result.get("recommendations", []), ensure_ascii=False),
        overall_match_percentage=overall_match,
    )
    db.add(skill_gap)
    resume.matching_score = overall_match / 100
    if resume.optimized_html:
        resume.optimized_html = re.sub(
            r'<div class="match-badge">匹配度: \d+%</div>',
            f'<div class="match-badge">匹配度: {overall_match}%</div>',
            resume.optimized_html,
        )
    db.commit()

    return {
        "overall_match_percentage": skill_gap.overall_match_percentage,
        "matching_skills": json.loads(skill_gap.matching_skills) if skill_gap.matching_skills else [],
        "gap_skills": json.loads(skill_gap.gap_skills) if skill_gap.gap_skills else [],
        "partial_skills": result.get("partial_skills", []),
        "recommendations": json.loads(skill_gap.recommendations) if skill_gap.recommendations else [],
    }


@router.get("/analysis/{resume_id}")
async def get_analysis(resume_id: int, db: Session = Depends(get_db)):
    skill_gap = db.query(SkillGap).filter(SkillGap.resume_id == resume_id).first()
    if not skill_gap:
        return JSONResponse(status_code=404, content={"error": "还未进行分析，请先提交分析请求"})

    return {
        "overall_match_percentage": skill_gap.overall_match_percentage,
        "matching_skills": json.loads(skill_gap.matching_skills) if skill_gap.matching_skills else [],
        "gap_skills": json.loads(skill_gap.gap_skills) if skill_gap.gap_skills else [],
        "recommendations": json.loads(skill_gap.recommendations) if skill_gap.recommendations else [],
    }
