import json
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Request, UploadFile, File, Form, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session

from app.config import UPLOAD_DIR, ALLOWED_IMAGE_EXTENSIONS, MAX_FILE_SIZE
from app.database import get_db
from app.models import Session as SessionModel, JobPosting
from app.services.ocr_service import ocr_image
from app.services.ai_service import AIService
from app.services.job_parser import JobParser

router = APIRouter(tags=["job"])

ai_service = AIService()
job_parser = JobParser(ai_service)


def get_session_id(request: Request) -> str:
    if "session_id" not in request.session:
        request.session["session_id"] = str(uuid.uuid4())
    return request.session["session_id"]


@router.post("/jobs")
async def create_job(
    request: Request,
    method: str = Form(...),
    text: str = Form(None),
    screenshot: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    session_id = get_session_id(request)

    db_session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not db_session:
        db_session = SessionModel(id=session_id)
        db.add(db_session)
        db.commit()

    raw_text = ""
    source_type = method

    if method == "text":
        if not text or not text.strip():
            return JSONResponse(status_code=400, content={"error": "请输入招聘要求文本"})
        raw_text = text.strip()
    elif method == "screenshot":
        if not screenshot:
            return JSONResponse(status_code=400, content={"error": "请上传截图文件"})

        file_ext = Path(screenshot.filename).suffix.lower()
        if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
            return JSONResponse(status_code=400, content={"error": "不支持的图片格式，请上传 PNG 或 JPG"})

        content = await screenshot.read()
        if len(content) > MAX_FILE_SIZE:
            return JSONResponse(status_code=400, content={"error": "文件大小超过 10MB 限制"})

        filename = f"{uuid.uuid4()}{file_ext}"
        filepath = os.path.join(UPLOAD_DIR, "screenshots", filename)
        with open(filepath, "wb") as f:
            f.write(content)

        raw_text = ocr_image(filepath)

    parsed = job_parser.parse(raw_text)

    job = JobPosting(
        session_id=session_id,
        raw_text=raw_text,
        source_type=source_type,
        company_name=parsed.get("company_name"),
        position=parsed.get("position"),
        salary_range=parsed.get("salary_range"),
        requirements=json.dumps(parsed.get("requirements_skills", []), ensure_ascii=False),
        responsibilities=json.dumps(parsed.get("responsibilities", []), ensure_ascii=False),
        raw_json=json.dumps(parsed, ensure_ascii=False),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    resp = RedirectResponse(url=f"/resume/input?job_id={job.id}", status_code=303)
    resp.headers["HX-Redirect"] = f"/resume/input?job_id={job.id}"
    return resp


@router.get("/jobs/{job_id}")
async def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job:
        return JSONResponse(status_code=404, content={"error": "职位不存在"})
    return {
        "id": job.id,
        "company_name": job.company_name,
        "position": job.position,
        "salary_range": job.salary_range,
        "requirements": json.loads(job.requirements) if job.requirements else [],
        "responsibilities": json.loads(job.responsibilities) if job.responsibilities else [],
        "raw_json": json.loads(job.raw_json) if job.raw_json else {},
        "source_type": job.source_type,
    }
