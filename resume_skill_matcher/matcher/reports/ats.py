def keyword_density(resume_text, jd_skills):
    resume_text = resume_text.lower()
    density = {}

    for skill in jd_skills:
        count = resume_text.count(skill.lower())
        density[skill] = count

    return density


def section_feedback(resume_text):
    feedback = []

    sections = ["experience", "projects", "skills", "education"]

    for section in sections:
        if section not in resume_text.lower():
            feedback.append(f"Consider adding a clear '{section.title()}' section.")

    return feedback
