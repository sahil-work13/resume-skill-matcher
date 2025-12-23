from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart


PAGE_WIDTH, PAGE_HEIGHT = A4


def draw_section_title(c, text, y):
    c.setFillColor(colors.HexColor("#1f2937"))  # dark gray
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, text)
    c.setFillColor(colors.black)
    return y - 22


def draw_badge(c, label, value, y):
    if value >= 75:
        bg = colors.green
    elif value >= 50:
        bg = colors.orange
    else:
        bg = colors.red

    c.setFillColor(bg)
    c.roundRect(50, y - 20, 120, 24, 6, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(110, y - 14, f"{label}: {value}%")
    c.setFillColor(colors.black)
    return y - 40


def draw_text_block(c, lines, y):
    c.setFont("Helvetica", 11)
    for line in lines:
        if y < 80:
            c.showPage()
            y = PAGE_HEIGHT - 60
        c.drawString(60, y, line)
        y -= 16
    return y


def draw_bar_chart(c, title, data_dict, y):
    if y < 300:
        c.showPage()
        y = PAGE_HEIGHT - 60

    drawing = Drawing(400, 200)
    chart = VerticalBarChart()
    chart.x = 50
    chart.y = 30
    chart.height = 150
    chart.width = 300
    chart.data = [list(data_dict.values())]
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = 100
    chart.valueAxis.valueStep = 20
    chart.categoryAxis.categoryNames = list(data_dict.keys())
    chart.bars[0].fillColor = colors.HexColor("#3b82f6")  # blue

    drawing.add(chart)

    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, title)
    drawing.drawOn(c, 30, y - 220)

    return y - 260


def generate_pdf_report(response, context):
    c = canvas.Canvas(response, pagesize=A4)
    y = PAGE_HEIGHT - 60

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "Resume Skill Match Report")
    y -= 40

    # Match Score Badge
    y = draw_badge(c, "Match Score", context["score"], y)

    # Confidence
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Confidence Level: {context['confidence_level']}")
    y -= 30

    # Skills
    y = draw_section_title(c, "Detected Skills", y)
    y = draw_text_block(c, [f"• {s}" for s in context["skills"]], y)

    y = draw_section_title(c, "Missing Skills", y)
    y = draw_text_block(c, [f"• {s}" for s in context["missing_skills"]], y)

    # Charts
    y = draw_bar_chart(c, "ATS Scorecard", context["ats_scores"], y)
    y = draw_bar_chart(c, "Section Score Breakdown", context["section_scores"], y)

    # Warnings
    y = draw_section_title(c, "Warnings & Insights", y)
    y = draw_text_block(c, [f"• {w['message']}" for w in context["warnings"]], y)

    # Recruiter Feedback
    y = draw_section_title(c, "Recruiter AI Feedback", y)
    y = draw_text_block(c, context["recruiter_feedback"].split("\n"), y)

    c.save()
