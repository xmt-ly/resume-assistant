# 更新日志

## v1.1.0 — 2026-05-17

### 新功能

- **用户认证系统**：支持手机号/邮箱注册、用户名登录、登出
- **管理员账号**：首次启动自动创建 `admin / admin123`
- **登录/注册页面**：Material Design 3 风格，支持密码可见性切换、微信登录入口（UI）

### 前端重构

- **Material Design 3 设计系统**：全部 6 个页面重构
  - 首页：Hero 区 + 双卡片选择 + 优势区 + Bento Grid
  - 职位输入：3-step stepper + 文本/截图双模式
  - 简历背景：上传/AI 生成双模式 + 背景表单
  - 简历预览：左栏 AI 建议 + 右栏 A4 预览 + 在线编辑
  - 技能分析：环形匹配图 + 技能列表 + AI 分析报告
- **全局组件**：导航栏、Footer、Toast 通知、加载弹窗

### 优化

- **加载状态统一**：所有页面加载状态改为全局模态弹窗，替代内联 spinner
- **输入提示优化**：修复 placeholder 与 label 重叠问题
- **清理英文文本**：移除/隐藏页面中多余的英文内容

### 本地化

- **字体本地化**：Inter（400/500/600）+ Material Symbols 图标，移除 Google CDN 依赖
- **系统字体兜底**：Noto Sans SC 改用 Microsoft YaHei 等系统字体

### 技术改进

- 新增 `bcrypt` 密码哈希
- 新增字体 MIME 类型注册（`.ttf` → `font/ttf`）
- 页面路由增加 `get_current_user()` 依赖

---

## v1.0.0 — 2026-05-17

### 初始版本

- FastAPI + Jinja2 + SQLAlchemy 后端
- AI 简历生成与优化（DeepSeek API）
- OCR 截图识别（EasyOCR + Tesseract）
- 技能差距分析
- PDF/DOCX/TXT 多格式下载
- Tailwind CSS 前端
