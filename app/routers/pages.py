import uuid

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Resume, JobPosting, SkillGap

router = APIRouter()


def get_templates(request: Request) -> Jinja2Templates:
    return request.app.state.templates


def get_session_id(request: Request) -> str:
    if "session_id" not in request.session:
        request.session["session_id"] = str(uuid.uuid4())
    return request.session["session_id"]


@router.get("/")
async def index(request: Request):
    session_id = get_session_id(request)
    templates = get_templates(request)
    return templates.TemplateResponse(request, "index.html", {"session_id": session_id})


@router.get("/job/input")
async def job_input(request: Request, method: str = "text"):
    session_id = get_session_id(request)
    templates = get_templates(request)
    return templates.TemplateResponse(
        request,
        "job_input.html",
        {"session_id": session_id, "method": method},
    )


@router.get("/resume/input")
async def resume_input(request: Request, job_id: int):
    session_id = get_session_id(request)
    templates = get_templates(request)

    db: Session = next(get_db())
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    db.close()

    if not job:
        return RedirectResponse(url="/job/input")

    return templates.TemplateResponse(
        request,
        "resume_input.html",
        {"session_id": session_id, "job": job},
    )


@router.get("/resume/preview/{resume_id}")
async def resume_preview(request: Request, resume_id: int):
    session_id = get_session_id(request)
    templates = get_templates(request)

    db: Session = next(get_db())
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    db.close()

    if not resume:
        return RedirectResponse(url="/")

    return templates.TemplateResponse(
        request,
        "preview.html",
        {"session_id": session_id, "resume": resume},
    )


@router.get("/analysis/{resume_id}")
async def analysis_page(request: Request, resume_id: int):
    session_id = get_session_id(request)
    templates = get_templates(request)

    db: Session = next(get_db())
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    db.close()

    if not resume:
        return RedirectResponse(url="/")

    return templates.TemplateResponse(
        request,
        "analysis.html",
        {"session_id": session_id, "resume": resume},
    )
