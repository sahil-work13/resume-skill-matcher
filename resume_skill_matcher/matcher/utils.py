# matcher/utils.py

import pdfplumber
import re
import docx
import os
from dotenv import load_dotenv
from skills.master_skills import MASTER_SKILLS
from google import genai
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# ---------------------------------------------------------
# ENV SETUP
# ---------------------------------------------------------
load_dotenv()
print("Gemini key loaded:", bool(os.environ.get("GEMINI_API_KEY")))
print("Gemini SDK path:", genai.__file__)

# ---------------------------------------------------------
# ROLE KEYWORDS
# ---------------------------------------------------------
ROLE_KEYWORDS = {
    "Data Scientist": [
        "data scientist", "machine learning", "statistics",
        "predictive modeling", "feature engineering", "python"
    ],
    "Data Analyst": [
        "data analyst", "sql", "excel", "power bi", "tableau"
    ],
    "Machine Learning Engineer": [
        "ml engineer", "model deployment", "tensorflow",
        "pytorch", "scikit-learn"
    ],
    "Backend Developer": [
        "backend", "django", "flask", "fastapi",
        "spring", "rest api", "microservices"
    ],
    "Frontend Developer": [
        "frontend", "react", "angular", "vue",
        "javascript", "html", "css"
    ],
    "Full Stack Developer": [
        "full stack", "frontend", "backend", "react", "node", "django"
    ],
    "Software Engineer": [
        "software engineer", "software developer",
        "data structures", "algorithms"
    ],
    "Java Developer": [
        "java", "spring", "spring boot", "hibernate"
    ],
    "Python Developer": [
        "python", "django", "flask", "automation"
    ],
}

# ---------------------------------------------------------
# TEXT EXTRACTION
# ---------------------------------------------------------
def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return re.sub(r"\s+", " ", text.lower())


def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)

    elif ext == ".docx":
        doc = docx.Document(file_path)
        return " ".join(p.text for p in doc.paragraphs).lower()

    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().lower()

    else:
        raise ValueError(f"Unsupported file format: {ext}")

# ---------------------------------------------------------
# SKILL EXTRACTION
# ---------------------------------------------------------
def extract_skills(text):
    found = set()
    text = text.lower()

    for skill, aliases in MASTER_SKILLS.items():
        for alias in aliases:
            if re.search(r"\b" + re.escape(alias) + r"\b", text):
                found.add(skill)

    return list(found)

# ---------------------------------------------------------
# SKILL MATCH SCORE
# ---------------------------------------------------------
def calculate_match_score(resume_skills, jd_skills):
    if not jd_skills:
        return min(60, len(resume_skills) * 5)

    common = set(resume_skills) & set(jd_skills)
    return round((len(common) / len(jd_skills)) * 100, 2)

# ---------------------------------------------------------
# ROLE DETECTION
# ---------------------------------------------------------
def detect_job_role(text):
    text = text.lower()
    scores = {}

    for role, keywords in ROLE_KEYWORDS.items():
        scores[role] = sum(1 for k in keywords if k in text)

    detected = max(scores, key=scores.get)
    return detected if scores[detected] > 0 else "Unknown"

# ---------------------------------------------------------
# SENIORITY DETECTION
# ---------------------------------------------------------
def detect_seniority(text):
    text = text.lower()

    if re.search(r"(intern|fresher)", text):
        return "Intern"
    if re.search(r"(junior|0-1 year|1 year)", text):
        return "Junior"
    if re.search(r"(2-4 years|mid)", text):
        return "Mid"
    if re.search(r"(senior|5\+ years|lead)", text):
        return "Senior"

    return "Unspecified"

# ---------------------------------------------------------
# REQUIREMENTS EXTRACTION
# ---------------------------------------------------------
REQUIREMENT_PATTERNS = [
    "experience", "knowledge of", "hands-on", "must have",
    "should have", "required", "responsible for",
    "ability to", "proficiency in"
]

def extract_requirements(jd_text):
    sentences = re.split(r"[.•\n]", jd_text)
    requirements = []

    for s in sentences:
        s = s.strip()
        if len(s) < 15:
            continue
        if any(p in s.lower() for p in REQUIREMENT_PATTERNS):
            requirements.append(s)

    return requirements

# ---------------------------------------------------------
# REQUIREMENT MATCH SCORE
# ---------------------------------------------------------
def requirement_match_score(resume_text, requirements):
    if not requirements:
        return 0

    resume_text = resume_text.lower()
    matched = 0

    for req in requirements:
        keywords = set(req.lower().split())
        if any(k in resume_text for k in keywords):
            matched += 1

    return round((matched / len(requirements)) * 100, 2)

# ---------------------------------------------------------
# ROLE FIT SCORE
# ---------------------------------------------------------
def role_fit_score(jd_role, resume_role):
    if jd_role == "Unknown" or resume_role == "Unknown":
        return 0
    return 100 if jd_role == resume_role else 40

# ---------------------------------------------------------
# ATS SCORECARD
# ---------------------------------------------------------
def ats_scorecard(resume_text, jd_text, resume_skills, jd_skills):
    scores = {}
    insights = []

    # Keyword Match
    keyword_score = (
        round((len(set(resume_skills) & set(jd_skills)) / len(jd_skills)) * 100, 2)
        if jd_skills else 60
    )
    scores["keyword_match"] = keyword_score

    if keyword_score < 50:
        insights.append("Low keyword match. Important job keywords are missing.")

    # Section Coverage
    sections = ["experience", "education", "skills", "projects", "summary"]
    section_hits = sum(1 for s in sections if s in resume_text)
    scores["section_coverage"] = round((section_hits / len(sections)) * 100, 2)

    # Skill Density
    skill_mentions = sum(resume_text.count(skill.lower()) for skill in resume_skills)
    scores["skill_relevance"] = min(100, skill_mentions * 6)

    # Readability
    sentences = re.split(r"[.!?]", resume_text)
    avg_len = sum(len(s.split()) for s in sentences if s.strip()) / max(len(sentences), 1)
    scores["readability"] = 85 if avg_len <= 20 else 70 if avg_len <= 30 else 50

    scores["overall"] = round(
        scores["keyword_match"] * 0.35 +
        scores["section_coverage"] * 0.2 +
        scores["skill_relevance"] * 0.25 +
        scores["readability"] * 0.2,
        2
    )

    return scores, insights

# ---------------------------------------------------------
# AI RECRUITER FEEDBACK (FINAL FIX)
# ---------------------------------------------------------
def recruiter_resume_feedback(resume_text, jd_text):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "AI feedback unavailable: API key not configured."

    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are a senior technical recruiter.
    Review the resume against the job description.
    Provide actionable ATS-friendly improvement suggestions.
    Give SHORT, SIMPLE, and CLEAR feedback.
    Do NOT use markdown, stars (*), hashes (#), or bullet symbols.
    Use plain text only.

    Structure the response EXACTLY like this:

    SECTION: Overall Fit
    (one short sentence)

    SECTION: Strengths
    - sentence
    - sentence

    SECTION: Improvements
    - sentence
    - sentence

    SECTION: Missing Skills (if any)
    - sentence
    - sentence

    Keep the response under 120 words.


        JOB DESCRIPTION:
        {jd_text[:1500]}

        RESUME:
        {resume_text[:1500]}
    """

    models = ["gemini-2.5-flash", "gemini-pro"]

    for model in models:
        for attempt in range(3):  # 🔁 retry 3 times
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                return response.text

            except Exception as e:
                error = str(e)
                if "503" in error or "overloaded" in error.lower():
                    time.sleep(2 * (attempt + 1))  # ⏳ backoff
                    continue
                else:
                    break  # different error → try next model

    return "AI feedback temporarily unavailable due to high load. Please try again."


def call_gemini(prompt):
    from google import genai
    import os, time

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    for model in ["gemini-2.5-flash", "gemini-pro"]:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            if "503" in str(e):
                time.sleep(2)
                continue
    return "AI service temporarily unavailable."

def rewrite_resume_bullets(resume_text, jd_text):
    prompt = f"""
    Rewrite weak resume bullet points into strong, ATS-friendly bullets.
    Use action verbs and metrics.
    Return 5 improved bullets only.
    Plain text only.

    JOB DESCRIPTION:
    {jd_text[:1200]}

    RESUME:
    {resume_text[:1200]}
    """
    return call_gemini(prompt)


def generate_skill_roadmap(missing_skills):
    roadmap = {}
    for skill in missing_skills:
        roadmap[skill] = [
            f"Learn fundamentals of {skill}",
            f"Build a small project using {skill}",
            f"Apply {skill} in a real-world scenario"
        ]
    return roadmap



def skill_gap_score(resume_text, jd_text):
    tfidf = TfidfVectorizer(stop_words="english")
    vectors = tfidf.fit_transform([resume_text, jd_text])
    similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
    return round((1 - similarity) * 100, 2)

def generate_mock_interview_questions(resume_text, jd_text):
    prompt = f"""
    Generate 5 technical interview questions based on the resume and job description.
    Mix theory + practical questions.
    Plain text, numbered list.

    JOB DESCRIPTION:
    {jd_text[:1200]}

    RESUME:
    {resume_text[:1200]}
    """
    return call_gemini(prompt)


def ats_keyword_suggestions(resume_text, jd_text):
    prompt = f"""
    Extract important ATS keywords from the job description
    that are missing or weak in the resume.
    Return as a simple list.

    JOB DESCRIPTION:
    {jd_text[:1200]}

    RESUME:
    {resume_text[:1200]}
    """
    return call_gemini(prompt)
