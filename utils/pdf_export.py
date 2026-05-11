from datetime import datetime
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, Spacer, PageBreak, BaseDocTemplate, PageTemplate, Frame


def _safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_\- ]+", "", value).strip()
    cleaned = re.sub(r"\s+", "_", cleaned)
    return cleaned or datetime.now().strftime("%Y%m%d_%H%M%S")

def header_footer(canvas, doc):
    canvas.saveState()
    
    # Header
    canvas.setFont("Helvetica-Bold", 14)
    canvas.setFillColor(colors.HexColor("#0b1220"))
    canvas.drawString(0.75 * inch, A4[1] - 0.6 * inch, "stayingahead")
    
    # Footer
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#64748b"))
    date_str = datetime.now().strftime("%d %b %Y").upper()
    
    canvas.drawString(0.75 * inch, 0.5 * inch, f"ISSUE 011 . {date_str}")
    
    # Page number centered
    page_num = f"{doc.page:02d}"
    canvas.drawCentredString(A4[0] / 2.0, 0.5 * inch, page_num)
    
    canvas.drawRightString(A4[0] - 0.75 * inch, 0.5 * inch, f"StayingAhead Daily . {date_str}")
    
    canvas.restoreState()


def export_digest_to_pdf(digest_text: str, output_dir: str = ".", category: str = "") -> str:
    """
    Convert plain-text digest output into a styled PDF matching StayingAhead format.
    """
    if not digest_text or not digest_text.strip():
        raise ValueError("Cannot export empty digest text.")

    lines = [line.rstrip() for line in digest_text.splitlines()]
    title = next((line for line in lines if line.strip() and not line.startswith("---")), "StayingAhead")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    category_prefix = f"{category.lower()}_" if category else ""
    filename = f"{category_prefix}{_safe_filename(title.lower())}_{timestamp}.pdf"
    output_path = Path(output_dir) / filename

    doc = BaseDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=1.0 * inch,
        bottomMargin=1.0 * inch,
        title="StayingAhead Daily",
        author="StayingAhead",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='StayingAhead', frames=frame, onPage=header_footer)
    doc.addPageTemplates([template])

    styles = getSampleStyleSheet()
    
    body = ParagraphStyle(
        "DigestBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        textColor=colors.HexColor("#334155"),
        spaceAfter=12,
    )
    
    article_number_style = ParagraphStyle(
        "ArticleNumber",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=colors.HexColor("#64748b"),
        spaceBefore=14,
        spaceAfter=4,
        textTransform="uppercase"
    )

    article_title_style = ParagraphStyle(
        "ArticleTitle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=0,
        spaceAfter=16,
    )

    heading = ParagraphStyle(
        "DigestHeading",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=12,
        textColor=colors.HexColor("#475569"),
        spaceBefore=14,
        spaceAfter=6,
        textTransform="uppercase"
    )

    bullet = ParagraphStyle(
        "DigestBullet",
        parent=body,
        leftIndent=14,
        bulletIndent=0,
        spaceAfter=4,
    )

    story = []
    
    inside_article = False

    for idx, raw_line in enumerate(lines):
        line = raw_line.strip()
        if not line:
            continue
            
        if line.startswith("---"):
            # Only add PageBreak if we've already started an article AND there are more lines coming
            if inside_article and any(l.strip() and not l.strip().startswith("---") for l in lines[idx+1:]):
                story.append(PageBreak())
            inside_article = True
            continue

        escaped = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        # Check for headings
        if re.match(r"^\d{2}\s*\.\s*[A-Z\s]+", line.upper()) or line.upper().startswith("EDITORIAL ."):
            story.append(Paragraph(escaped, article_number_style))
            continue
            
        if line.upper() in {
            "QUICK TAKE", "WHAT YOU NEED TO KNOW", "WHY IT MATTERS", "THE BIG PICTURE", 
            "THE LONG ARC", "WHAT TO WATCH", "DO THIS TODAY", "IF YOU TAKE ONE THING FROM THIS", 
            "AI DIGEST . LAST 24 HOURS", "SPORTS DIGEST . LAST 24 HOURS", "FINANCE DIGEST . LAST 24 HOURS",
            "POLITICS DIGEST . LAST 24 HOURS", "INCIDENTS DIGEST . LAST 24 HOURS", "GENERAL DIGEST . LAST 24 HOURS",
            "T O D AY ' S  H E A D L I N E", "SENT BY", "WHAT WE COVER TODAY."
        }:
            story.append(Paragraph(escaped, heading))
            continue

        # If it's the line immediately after an article number, it's usually the title
        if story and story[-1].style.name == "ArticleNumber":
            story.append(Paragraph(escaped, article_title_style))
            continue

        if line.startswith("- ") or line.startswith("* "):
            bullet_text = escaped[2:].strip()
            # Handle markdown bold
            bullet_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", bullet_text)
            story.append(Paragraph(bullet_text, bullet, bulletText="•"))
            continue

        # Normal text, handle markdown bold
        escaped = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", escaped)
        story.append(Paragraph(escaped, body))

    doc.build(story)
    return str(output_path.resolve())

