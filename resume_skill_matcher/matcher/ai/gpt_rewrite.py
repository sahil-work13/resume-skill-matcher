import openai

def rewrite_resume_section(text, jd_text):
    prompt = f"""
Rewrite the following resume content to better match this job description.

JOB DESCRIPTION:
{jd_text}

RESUME CONTENT:
{text}

Rules:
- Keep facts unchanged
- Improve clarity & impact
- Use ATS-friendly keywords
"""

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    return response.choices[0].message.content
