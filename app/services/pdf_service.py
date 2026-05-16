import logging
import os

logger = logging.getLogger(__name__)

PDF_CSS = """
@page {
    size: A4;
    margin: 2cm 2.5cm;
}
body {
    font-family: 'Noto Sans SC', 'Source Han Sans SC', sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
}
h1 { font-size: 18pt; text-align: center; margin-bottom: 4pt; }
h2 { font-size: 13pt; border-bottom: 1px solid #ccc; padding-bottom: 3pt; margin-top: 16pt; margin-bottom: 8pt; }
h3 { font-size: 11pt; margin-top: 10pt; margin-bottom: 4pt; }
p { margin: 4pt 0; }
.section { margin-bottom: 12pt; }
.match-badge { text-align: center; font-size: 9pt; color: #2563eb; margin-bottom: 12pt; }
.skill-tag { display: inline; font-size: 9pt; color: #2563eb; }
.tags { margin-bottom: 12pt; }
.resume-body { white-space: pre-wrap; }
br { display: block; margin: 4pt 0; }
"""


class PDFService:
    def __init__(self):
        self._weasyprint_available = None

    def _check_weasyprint(self) -> bool:
        if self._weasyprint_available is None:
            try:
                import weasyprint
                self._weasyprint_available = True
            except Exception as e:
                logger.warning(f"WeasyPrint not available: {e}")
                self._weasyprint_available = False
        return self._weasyprint_available

    def generate(self, title: str, body_html: str) -> bytes:
        if self._check_weasyprint():
            return self._generate_with_weasyprint(title, body_html)
        else:
            return self._generate_with_reportlab(title, body_html)

    def _generate_with_weasyprint(self, title: str, body_html: str) -> bytes:
        import weasyprint

        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>{PDF_CSS}</style>
</head>
<body>
{body_html}
</body>
</html>"""

        font_dirs = [
            "fonts",
            os.path.join(os.path.dirname(__file__), "..", "..", "fonts"),
        ]
        for font_dir in font_dirs:
            abs_dir = os.path.abspath(font_dir)
            if os.path.isdir(abs_dir):
                for f in os.listdir(abs_dir):
                    if f.endswith((".ttf", ".otf", ".woff", ".woff2")):
                        font_path = os.path.join(abs_dir, f)
                        font_name = os.path.splitext(f)[0]
                        html_content = html_content.replace(
                            "</style>",
                            f"@font-face {{ font-family: '{font_name}'; src: url('file:///{font_path.replace(chr(92), '/')}'); }}\n</style>",
                        )
                        html_content = html_content.replace(
                            "font-family: 'Noto Sans SC'",
                            f"font-family: '{font_name}'",
                        )
                        break

        pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
        return pdf_bytes

    def _init_reportlab_font(self) -> str:
        try:
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont

            # Try common YaHei font paths on Windows
            candidates = [
                (r"C:\Windows\Fonts\msyh.ttc", 0),
                (r"C:\Windows\Fonts\msyh.ttf", None),
            ]
            for path, subfont in candidates:
                if os.path.isfile(path):
                    kwargs = {"filename": path}
                    if subfont is not None:
                        kwargs["subfontIndex"] = subfont
                    pdfmetrics.registerFont(TTFont("MicrosoftYaHei", **kwargs))
                    logger.info(f"ReportLab: registered MicrosoftYaHei from {path}")
                    return "MicrosoftYaHei"
        except Exception as e:
            logger.warning(f"ReportLab font registration failed: {e}")
        return "Helvetica"

    def _generate_with_reportlab(self, title: str, body_html: str) -> bytes:
        from io import BytesIO
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        import re

        font_name = self._init_reportlab_font()

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4,
            topMargin=2 * cm, bottomMargin=2 * cm,
            leftMargin=2.5 * cm, rightMargin=2.5 * cm,
        )

        s_normal = ParagraphStyle("Normal", fontName=font_name, fontSize=11, leading=16, spaceAfter=4)
        s_heading = ParagraphStyle("Heading", fontName=font_name, fontSize=14, leading=20, spaceBefore=12, spaceAfter=6)
        s_title = ParagraphStyle("Title", fontName=font_name, fontSize=18, leading=24, alignment=TA_CENTER, spaceAfter=12)
        s_bullet = ParagraphStyle("Bullet", fontName=font_name, fontSize=11, leading=16, leftIndent=12, spaceAfter=2)

        story = [Paragraph(title, s_title)]

        for line in body_html.split("\n"):
            line = line.strip()
            if not line:
                continue

            m = re.match(r"<h([12])>(.*?)</h\1>", line)
            if m:
                story.append(Paragraph(m.group(2), s_heading))
                continue

            m = re.match(r"<p>• (.+?)</p>", line)
            if m:
                story.append(Paragraph(f"&bull; {m.group(1)}", s_bullet))
                continue

            m = re.match(r"<p>(.+?)</p>", line)
            if m:
                story.append(Paragraph(m.group(1), s_normal))
                continue

            text = re.sub(r"<[^>]+>", "", line)
            if text:
                story.append(Paragraph(text, s_normal))

        doc.build(story)
        return buffer.getvalue()
