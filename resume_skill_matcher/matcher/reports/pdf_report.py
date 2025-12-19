from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from .insights import generate_resume_insights
from .comparison import compare_resume_vs_jd

def generate_pdf_report(response, score, skills, missing_skills):
    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "Resume–JD Match Report")

    # Score
    c.setFont("Helvetica-Bold", 42)
    c.setFillColor(HexColor("#4f46e5"))
    c.drawString(50, height - 120, f"{score}%")

    # Progress Bar
    c.setFillColor(HexColor("#e5e7eb"))
    c.rect(50, height - 150, 400, 12, fill=1)
    c.setFillColor(HexColor("#6366f1"))
    c.rect(50, height - 150, int(4 * score), 12, fill=1)

    # Skills
    y = height - 190
    c.setFillColor(HexColor("#000000"))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Matched Skills")
    y -= 20

    for s in skills[:10]:
        c.setFont("Helvetica", 11)
        c.drawString(60, y, f"• {s}")
        y -= 14

    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Missing Skills")
    y -= 20

    for m in missing_skills[:10]:
        c.setFont("Helvetica", 11)
        c.drawString(60, y, f"• {m}")
        y -= 14

    # Insights
    suggestions, ats_notes = generate_resume_insights(score, missing_skills)

    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Resume Improvement Suggestions")
    y -= 20

    for tip in suggestions:
        c.setFont("Helvetica", 11)
        c.drawString(60, y, f"• {tip}")
        y -= 16

    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "ATS Explanation")
    y -= 20

    for note in ats_notes:
        c.setFont("Helvetica", 11)
        c.drawString(60, y, f"• {note}")
        y -= 16

    c.showPage()
    c.save()
