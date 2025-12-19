def generate_resume_insights(score, missing_skills):
    suggestions = []

    if score < 40:
        suggestions.append(
            "Low ATS alignment. Add missing keywords and tailor resume for this role."
        )
    elif score < 70:
        suggestions.append(
            "Moderate ATS alignment. Improve project descriptions using job keywords."
        )
    else:
        suggestions.append(
            "Strong ATS alignment. Minor refinements can further boost ranking."
        )

    if missing_skills:
        suggestions.append(
            "Recommended skills to add: " + ", ".join(missing_skills[:5])
        )

    ats_notes = [
        "ATS systems prioritize keyword relevance over formatting.",
        "Your score reflects overlap between resume and job description skills.",
        "Missing keywords reduce ATS visibility even if you have experience."
    ]

    return suggestions, ats_notes
