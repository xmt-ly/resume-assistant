from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import bcrypt
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

router = APIRouter()


def get_templates(request: Request) -> Jinja2Templates:
    return request.app.state.templates


def get_current_user(request: Request) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    db: Session = next(get_db())
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()


@router.get("/login")
async def login_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=303)
    templates = get_templates(request)
    return templates.TemplateResponse(request, "login.html", {"user": user})


@router.get("/register")
async def register_page(request: Request):
    user = get_current_user(request)
    if user:
        return RedirectResponse(url="/", status_code=303)
    templates = get_templates(request)
    return templates.TemplateResponse(request, "register.html", {"user": user})


@router.post("/register")
async def register(
    request: Request,
    phone: str = Form(default=""),
    email: str = Form(default=""),
    password: str = Form(...),
    confirm_password: str = Form(default=""),
):
    templates = get_templates(request)
    db: Session = next(get_db())

    try:
        # Validate passwords match
        if password != confirm_password:
            return templates.TemplateResponse(
                request,
                "register.html",
                {"user": None, "error": "两次密码不一致"},
                status_code=400,
            )

        # At least one of phone or email must be provided
        if not phone and not email:
            return templates.TemplateResponse(
                request,
                "register.html",
                {"user": None, "error": "请填写手机号或邮箱"},
                status_code=400,
            )

        # Check if phone already exists
        if phone:
            existing = db.query(User).filter(User.phone == phone).first()
            if existing:
                return templates.TemplateResponse(
                    request,
                    "register.html",
                    {"user": None, "error": "该手机号已注册"},
                    status_code=400,
                )

        # Check if email already exists
        if email:
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                return templates.TemplateResponse(
                    request,
                    "register.html",
                    {"user": None, "error": "该邮箱已注册"},
                    status_code=400,
                )

        # Create user
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        if phone:
            username = f"用户{phone[-4:]}"
        else:
            username = email.split("@")[0]
        user = User(
            username=username,
            phone=phone or None,
            email=email or None,
            password_hash=password_hash,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return RedirectResponse(url="/auth/login", status_code=303)
    finally:
        db.close()


@router.post("/login")
async def login(
    request: Request,
    identifier: str = Form(...),
    password: str = Form(...),
):
    templates = get_templates(request)
    db: Session = next(get_db())

    try:
        # Find user by phone, email, or username
        user = db.query(User).filter(
            (User.phone == identifier) | (User.email == identifier) | (User.username == identifier)
        ).first()

        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return templates.TemplateResponse(
                request,
                "login.html",
                {"user": None, "error": "手机号或密码错误"},
                status_code=400,
            )

        # Set session
        request.session["user_id"] = user.id
        return RedirectResponse(url="/", status_code=303)
    finally:
        db.close()


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)
