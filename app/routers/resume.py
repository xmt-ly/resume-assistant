import json
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Request, UploadFile, File, Form, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from app.config import ALLOWED_RESUME_EXTENSIONS, MAX_FILE_SIZE, UPLOAD_DIR
from app.database import get_db
from app.models import Session as SessionModel, JobPosting, Resume
from app.services.ai_service import AIService
from app.services.resume_optimizer import ResumeOptimizer

router = APIRouter(tags=["resume"])

ai_service = AIService()
resume_optimizer = ResumeOptimizer(ai_service)


def read_resume_file(filepath: str) -> str:
    ext = Path(filepath).suffix.lower()
    if ext == ".txt":
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    elif ext == ".docx":
        from docx import Document
        doc = Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs)
    elif ext == ".pdf":
        import fitz
        doc = fitz.open(filepath)
        return "\n".join(page.get_text() for page in doc)
    return ""


def generate_resume_html(job_data: dict, optimized_text: str, matching_score: float, highlighted_skills: list) -> str:
    position = job_data.get("position", "")
    company = job_data.get("company_name", "")
    name = (optimized_text or "").split("\n")[0].strip() or "个人简历"
    skills_html = ""
    if highlighted_skills:
        skills_html = '<div class="skills-section"><h3>核心匹配技能</h3><div class="skills-tags">' + \
                      "".join(f'<span class="skill-tag">{s}</span>' for s in highlighted_skills) + \
                      '</div></div>'

    return f"""<div class="resume-card">
  <div class="resume-header">
    <h1 class="resume-name">{name}</h1>
    <p class="resume-target">目标: {position} @ {company}</p>
    <div class="match-badge">匹配度: {matching_score * 100:.0f}%</div>
  </div>
  {skills_html}
  <div class="resume-body">
    {optimized_text.replace(chr(10), '<br>')}
  </div>
</div>"""


def extract_skills_from_resume(optimized_text: str) -> list:
    return [s.strip() for s in optimized_text.split() if len(s.strip()) > 1][:20]


@router.post("/resumes")
async def create_resume(
    request: Request,
    job_id: int = Form(...),
    source_type: str = Form("upload"),
    resume_file: UploadFile = File(None),
    background: str = Form(None),
    db: Session = Depends(get_db),
):
    session_id = request.session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session["session_id"] = session_id

    db_session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not db_session:
        db_session = SessionModel(id=session_id)
        db.add(db_session)
        db.commit()

    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        return JSONResponse(status_code=404, content={"error": "职位不存在"})

    job_data = {
        "position": job.position,
        "company_name": job.company_name,
        "salary_range": job.salary_range,
        "requirements_skills": json.loads(job.requirements) if job.requirements else [],
    }

    original_text = ""
    original_file_path = None

    if source_type == "upload":
        if not resume_file or not resume_file.filename:
            return JSONResponse(status_code=400, content={"error": "请选择要上传的简历文件"})
        ext = Path(resume_file.filename).suffix.lower()
        if ext not in ALLOWED_RESUME_EXTENSIONS:
            return JSONResponse(status_code=400, content={"error": "不支持的简历格式，请上传 PDF、DOCX 或 TXT 文件"})

        content = await resume_file.read()
        if len(content) > MAX_FILE_SIZE:
            return JSONResponse(status_code=400, content={"error": "文件大小超过 10MB 限制"})

        filename = f"{uuid.uuid4()}{ext}"
        filepath = os.path.join(UPLOAD_DIR, "resumes", filename)
        with open(filepath, "wb") as f:
            f.write(content)

        original_text = read_resume_file(filepath)
        original_file_path = filepath
        result = resume_optimizer.optimize(original_text, job_data)
    else:
        if not background or not background.strip():
            return JSONResponse(status_code=400, content={"error": "请填写你的工作背景信息"})
        original_text = background.strip()
        result = resume_optimizer.generate_from_scratch(original_text, job_data)

    resume = Resume(
        session_id=session_id,
        job_posting_id=job_id,
        source_type=source_type,
        original_text=original_text,
        original_file_path=original_file_path,
        optimized_text=result["optimized_text"],
        matching_score=result["matching_score"],
        improvements=json.dumps(result.get("improvements", []), ensure_ascii=False),
    )
    resume.optimized_html = generate_resume_html(
        job_data, result["optimized_text"], result["matching_score"],
        result.get("highlighted_skills", []),
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    resp = RedirectResponse(url=f"/resume/preview/{resume.id}", status_code=303)
    resp.headers["HX-Redirect"] = f"/resume/preview/{resume.id}"
    return resp


@router.put("/resumes/{resume_id}")
async def update_resume(resume_id: int, request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        return JSONResponse(status_code=404, content={"error": "简历不存在"})

    new_text = body.get("optimized_text", resume.optimized_text)
    resume.optimized_text = new_text

    # 重建 optimized_html 保持结构完整
    job = None
    if resume.job_posting_id:
        job = db.query(JobPosting).filter(JobPosting.id == resume.job_posting_id).first()

    job_data = {
        "position": job.position if job else "",
        "company_name": job.company_name if job else "",
        "requirements_skills": [],
    }
    resume.optimized_html = generate_resume_html(
        job_data, new_text, resume.matching_score or 0, [],
    )

    db.commit()
    return {"status": "ok"}


@router.get("/resumes/{resume_id}/html")
async def get_resume_html(resume_id: int, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not resume:
        return JSONResponse(status_code=404, content={"error": "简历不存在"})
    return {"html": resume.optimized_html or "", "matching_score": resume.matching_score}
