def build_resume_context(resume_data):
    return f"""
Candidate Resume Summary:
Skills: {', '.join(resume_data.get('skills', []))}
Experience: {resume_data.get('experience', '')}
Education: {resume_data.get('education', '')}
ATS Score: {resume_data.get('ats_score', 0)}
Role Match: {resume_data.get('role', '')}
"""
