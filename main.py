import json
import mimetypes
import os
import uuid
from contextlib import asynccontextmanager

# Register font MIME types (Python's mimetypes module doesn't know these)
mimetypes.add_type("font/ttf", ".ttf")
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("font/woff", ".woff")

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import SESSION_SECRET
from app.database import init_db
from app.models import User
from app.routers import pages, job, resume, analysis, download, auth


def from_json_filter(value):
    if isinstance(value, str):
        return json.loads(value)
    return value or []


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    os.makedirs("uploads/screenshots", exist_ok=True)
    os.makedirs("uploads/resumes", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    os.makedirs("fonts", exist_ok=True)

    # Create admin account if not exists
    from app.database import SessionLocal
    import bcrypt as _bcrypt
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin_pw = _bcrypt.hashpw("admin123".encode("utf-8"), _bcrypt.gensalt()).decode("utf-8")
            admin = User(username="admin", email="admin@resume.local", password_hash=admin_pw)
            db.add(admin)
            db.commit()
            print("[INFO] 管理员账号已创建: admin / admin123")
    finally:
        db.close()

    yield


app = FastAPI(title="简历助手", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

templates = Jinja2Templates(directory="app/templates")
templates.env.filters["from_json"] = from_json_filter
app.state.templates = templates

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages.router)
app.include_router(auth.router, prefix="/auth")
app.include_router(job.router, prefix="/api")
app.include_router(resume.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(download.router, prefix="/api")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import logging
    logging.error(f"Unhandled error: {exc}", exc_info=True)
    try:
        user = None
        user_id = request.session.get("user_id") if hasattr(request, "session") else None
        if user_id:
            from app.database import SessionLocal
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == user_id).first()
            finally:
                db.close()
        return templates.TemplateResponse(
            request,
            "base.html",
            {
                "session_id": request.session.get("session_id", ""),
                "user": user,
                "content": f'<div class="text-center py-20"><p class="text-red-500 text-lg">出错了: {str(exc)}</p><a href="/" class="text-blue-500 underline mt-4 inline-block">返回首页</a></div>',
            },
        )
    except Exception:
        from fastapi.responses import HTMLResponse
        return HTMLResponse(
            content=f"<html><body><h1>服务器错误</h1><p>{str(exc)}</p></body></html>",
            status_code=500,
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
