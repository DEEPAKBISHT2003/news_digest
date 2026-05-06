from datetime import datetime
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


def _safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_\- ]+", "", value).strip()
    cleaned = re.sub(r"\s+", "_", cleaned)
    return cleaned or datetime.now().strftime("%Y%m%d_%H%M%S")


def export_digest_to_pdf(digest_text: str, output_dir: str = ".") -> str:
    """
    Convert plain-text digest output into a styled PDF and return file path.
    """
    if not digest_text or not digest_text.strip():
        raise ValueError("Cannot export empty digest text.")

    lines = [line.rstrip() for line in digest_text.splitlines()]
    title = next((line for line in lines if line.strip()), "MORNING DIGEST")
    filename = f"{_safe_filename(title.lower())}.pdf"
    output_path = Path(output_dir) / filename

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=title,
        author="AI Daily Digest",
    )

    styles = getSampleStyleSheet()
    body = ParagraphStyle(
        "DigestBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#111827"),
        spaceAfter=4,
    )
    heading = ParagraphStyle(
        "DigestHeading",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=10,
        spaceAfter=6,
    )
    title_style = ParagraphStyle(
        "DigestTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0b1220"),
        spaceAfter=12,
    )
    bullet = ParagraphStyle(
        "DigestBullet",
        parent=body,
        leftIndent=12,
        bulletIndent=0,
        spaceAfter=2,
    )

    story = []
    title_rendered = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            story.append(Spacer(1, 6))
            continue

        escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        if not title_rendered and line.upper().startswith("MORNING DIGEST"):
            story.append(Paragraph(escaped, title_style))
            title_rendered = True
            continue

        if re.match(r"^\d{2}\.\s", line) or line in {"QUICK TAKE:", "WHAT YOU NEED TO KNOW:", "SOURCE:", "Insights:", "Editorial Take:", "What we cover today:"}:
            story.append(Paragraph(escaped, heading))
            continue

        if line.startswith("- "):
            bullet_text = escaped[2:].strip()
            story.append(Paragraph(bullet_text, bullet, bulletText="•"))
            continue

        story.append(Paragraph(escaped, body))

    doc.build(story)
    return str(output_path.resolve())

