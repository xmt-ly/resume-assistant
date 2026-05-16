import json
import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import SESSION_SECRET
from app.database import init_db
from app.routers import pages, job, resume, analysis, download


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
    yield


app = FastAPI(title="简历助手", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

templates = Jinja2Templates(directory="app/templates")
templates.env.filters["from_json"] = from_json_filter
app.state.templates = templates

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages.router)
app.include_router(job.router, prefix="/api")
app.include_router(resume.router, prefix="/api")
app.include_router(analysis.router, prefix="/api")
app.include_router(download.router, prefix="/api")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import logging
    logging.error(f"Unhandled error: {exc}", exc_info=True)
    try:
        session_id = request.session.get("session_id", "") if hasattr(request, "session") else ""
        return templates.TemplateResponse(
            request,
            "base.html",
            {
                "session_id": session_id,
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
