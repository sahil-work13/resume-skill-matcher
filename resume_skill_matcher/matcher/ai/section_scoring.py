def score_resume_sections(resume_text):
    sections = {
        "skills": ["skills", "technologies"],
        "experience": ["experience", "work history"],
        "projects": ["projects"],
        "education": ["education"]
    }

    scores = {}

    for section, keywords in sections.items():
        found = any(k in resume_text.lower() for k in keywords)
        scores[section] = 90 if found else 40

    return scores
