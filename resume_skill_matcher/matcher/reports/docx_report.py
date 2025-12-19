from docx import Document


def generate_docx_report(response, score, skills, missing_skills):
    doc = Document()

    doc.add_heading("Resume Skill Match Report", level=1)
    doc.add_paragraph(f"Match Score: {score}%")

    doc.add_heading("Detected Skills", level=2)
    for skill in skills:
        doc.add_paragraph(skill, style="List Bullet")

    doc.add_heading("Missing / Recommended Skills", level=2)
    for skill in missing_skills:
        doc.add_paragraph(skill, style="List Bullet")

    doc.save(response)
