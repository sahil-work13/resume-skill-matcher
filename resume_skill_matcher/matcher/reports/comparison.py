def compare_resume_vs_jd(resume_skills, jd_skills):
    matched = list(set(resume_skills) & set(jd_skills))
    missing = list(set(jd_skills) - set(resume_skills))

    return {
        "matched": matched,
        "missing": missing
    }
