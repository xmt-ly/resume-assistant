# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

简历助手 (Resume Assistant) — 用户提交 Boss 直聘招聘要求（文本或截图），AI 帮助生成高度匹配的简历和技能提升建议。

## Python Environment

- **Python interpreter**: `D:\Anaconda3\envs\face_env` (Conda, Python 3.12)
- **Package management**: `pip install -r requirements.txt`

## Commands

```bash
# Run the application (with auto-reload via WatchFiles)
python main.py            # http://localhost:8000

# Install dependencies
pip install -r requirements.txt

# Additional required packages (not in requirements.txt)
pip install reportlab     # PDF fallback (WeasyPrint unavailable on Windows)

# Test AI features with curl
curl http://127.0.0.1:8000/api/jobs/1        # Get job posting
curl -X POST http://127.0.0.1:8000/api/analysis/1    # Trigger skill gap analysis
```

## Environment Variables (`.env`)

```
AI_PROXY_URL=https://api.deepseek.com/v1   # OpenAI-compatible API endpoint
AI_API_KEY=sk-xxx                           # API key
AI_MODEL=deepseek-chat                      # Model name
DATABASE_URL=sqlite:///./data/resume_assistant.db
UPLOAD_DIR=./uploads
SESSION_SECRET=resume-assistant-secret-key
```

## Architecture

**Backend**: FastAPI + Jinja2 templates
**Database**: SQLite + SQLAlchemy ORM
**OCR**: EasyOCR (ch_sim+en) with Tesseract fallback
**PDF**: WeasyPrint (HTML→PDF) with ReportLab fallback
**AI**: OpenAI SDK → DeepSeek API (OpenAI-compatible)

**Frontend**: 100% vanilla JS — no framework. `Tailwind CSS` loaded from `/static/js/tailwind.min.js` for utility styles. All pages use standard HTML forms, `fetch()` API, and inline event handlers. `window.showToast(msg, type)` is defined in `base.html` for global notifications.

## Key Data Flow

1. User pastes text or uploads screenshot → `POST /api/jobs`
2. OCR extracts text (screenshots) → AI extracts structured data (company, position, skills)
3. User uploads resume or fills background → `POST /api/resumes`
4. AI optimizes resume (or generates from scratch) → stores `optimized_text`
5. Preview page shows result with match score → user can edit online
6. `POST /api/analysis/{id}` → AI analyzes skill gaps → returns matching/gap skills + recommendations
7. `GET /api/download/{id}` → generates and downloads PDF

## Critical Patterns

### Resume name from first line
The resume display name is extracted from the **first line** of `optimized_text` (`resume.py:_generate_resume_html`, `download.py:_build_body_html`). This means editing the first line in the preview editor changes the name shown in the header and all downloads.

### optimized_text is the canonical source of truth
`optimized_text` drives everything: preview HTML, all downloads (TXT/PDF/DOCX), and the name header. `optimized_html` is derived from it via `generate_resume_html()`. The `PUT /api/resumes/{id}` endpoint regenerates `optimized_html` from `optimized_text` — the frontend only sends `{optimized_text: newText}`.

### Resume input mode routing (`source_type`)
The `POST /api/resumes` endpoint uses an explicit `source_type` form field (`"upload"` or `"generate"`) to decide whether to read a file or generate from scratch. This avoids browser quirks where empty `<input type="file">` fields are still sent with the form.

### AI prompts
Three core prompts in `resume_optimizer.py` + `job_parser.py` (all use `response_format={"type": "json_object"}`):
- **job extraction** (`job_parser.py`): raw text → {company, position, salary, skills, responsibilities, education}
- **resume optimization** (`resume_optimizer.py:OPTIMIZE_PROMPT`): resume + job data → {optimized_text, matching_score, improvements, highlighted_skills}
- **skill gap analysis** (`resume_optimizer.py:SKILL_GAP_PROMPT`): resume text vs job requirements → {matching_skills, gap_skills, recommendations, overall_match_percentage}

### Download format routing
`GET /api/download/{resume_id}?format=pdf|txt|docx`
- **PDF**: WeasyPrint (primary) → ReportLab fallback on Windows. HTML body built by `_build_body_html()`.
- **DOCX**: python-docx with `_set_font()` helper (sets w:ascii, w:hAnsi, w:eastAsia XML attributes to "Microsoft YaHei").
- **TXT**: Plain text with header section.
- Content-Disposition uses RFC 5987 `filename*=UTF-8''` for Chinese filenames.

### _set_font() for DOCX Chinese text
In `download.py`, `_set_font(run)` is required for every text run in a DOCX to render Chinese properly. It sets both Western (`w:ascii`, `w:hAnsi`) and East-Asian (`w:eastAsia`) font attributes via XML. This must be called on each `run` and on the `Normal` style itself.

### Toast notifications
`window.showToast(msg, type)` is available globally (defined in `base.html`). Types: `'success'`, `'error'`, `'info'`. Auto-hides after 4 seconds.

## Important Notes

- **Starlette 1.0.0** `TemplateResponse` signature: `templates.TemplateResponse(request, "template.html", context_dict)` — the `request` parameter is required as the first positional arg.
- Session is managed via `starlette.middleware.sessions.SessionMiddleware` (cookie-based).
- Add custom Jinja2 filters in `main.py` via `templates.env.filters["name"] = func` — one filter `from_json` is already registered.
- **EasyOCR lazy loading**: The first OCR call downloads model files (~1-2 min on first run). Subsequent calls are fast.
- The `static/js/` directory contains a local copy of `tailwind.min.js` (CDN scripts are unreliable from China).
- **ReportLab on Windows**: Requires `pip install reportlab` (not in requirements.txt). Font is loaded from `C:\Windows\Fonts\msyh.ttc` (subfontIndex=0). Without it, Helvetica is used and Chinese text renders as boxes.
- **DB Schema**: 4 tables — `sessions` (session tracking), `job_postings` (parsed job data with JSON fields), `resumes` (original + optimized text/html, matching_score), `skill_gaps` (matching/gap skills, recommendations). JSON fields stored as Text (JSON serialized).