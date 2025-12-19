# matcher/utils.py
import pdfplumber
import re
import docx
import os
from skills.master_skills import MASTER_SKILLS
from dotenv import load_dotenv


load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
print("HF TOKEN CHECK:", HF_API_KEY[:10] if HF_API_KEY else "NOT FOUND")

# =========================================================
# ROLE KEYWORDS (UNCHANGED – GOOD)
# =========================================================
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

# =========================================================
# TEXT EXTRACTION
# =========================================================
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

# =========================================================
# SKILL EXTRACTION
# =========================================================
def extract_skills(text):
    found = set()
    text = text.lower()

    for skill, aliases in MASTER_SKILLS.items():
        for alias in aliases:
            if re.search(r"\b" + re.escape(alias) + r"\b", text):
                found.add(skill)

    return list(found)

# =========================================================
# SKILL MATCH SCORE
# =========================================================
def calculate_match_score(resume_skills, jd_skills):
    if not jd_skills:
        return min(60, len(resume_skills) * 5)

    common = set(resume_skills) & set(jd_skills)
    return round((len(common) / len(jd_skills)) * 100, 2)

# =========================================================
# ROLE DETECTION (JD + RESUME)
# =========================================================
def detect_job_role(text):
    text = text.lower()
    scores = {}

    for role, keywords in ROLE_KEYWORDS.items():
        scores[role] = sum(1 for k in keywords if k in text)

    detected = max(scores, key=scores.get)
    return detected if scores[detected] > 0 else "Unknown"

# =========================================================
# SENIORITY DETECTION
# =========================================================
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

# =========================================================
# REQUIREMENT EXTRACTION (FIXED)
# =========================================================
REQUIREMENT_PATTERNS = [
    "experience", "knowledge of", "hands-on", "must have",
    "should have", "required", "responsible for",
    "ability to", "proficiency in"
]

def extract_requirements(jd_text):
    # Keep sentence structure
    sentences = re.split(r"[.•\n]", jd_text)
    requirements = []

    for s in sentences:
        s = s.strip()
        if len(s) < 15:
            continue
        if any(p in s.lower() for p in REQUIREMENT_PATTERNS):
            requirements.append(s)

    return requirements


# =========================================================
# REQUIREMENT MATCH SCORE (REAL)
# =========================================================
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

# =========================================================
# ROLE FIT SCORE
# =========================================================
def role_fit_score(jd_role, resume_role):
    if jd_role == "Unknown" or resume_role == "Unknown":
        return 0
    return 100 if jd_role == resume_role else 40


import re

def ats_scorecard(resume_text, jd_text, resume_skills, jd_skills):
    scores = {}
    insights = []

    # 1️⃣ Keyword Match
    if jd_skills:
        keyword_score = round((len(set(resume_skills) & set(jd_skills)) / len(jd_skills)) * 100, 2)
    else:
        keyword_score = 60

    scores["keyword_match"] = keyword_score

    if keyword_score < 50:
        insights.append("Low keyword match. Important job keywords are missing from the resume.")

    # 2️⃣ Section Coverage
    sections = ["experience", "education", "skills", "projects", "summary"]
    section_hits = sum(1 for s in sections if s in resume_text.lower())
    section_score = round((section_hits / len(sections)) * 100, 2)

    scores["section_coverage"] = section_score

    if section_score < 60:
        insights.append("Some important resume sections are missing or not clearly labeled.")

    # 3️⃣ Skill Relevance Density
    words = resume_text.lower().split()
    skill_mentions = sum(words.count(skill.lower()) for skill in resume_skills)

    relevance_score = min(100, skill_mentions * 6)
    scores["skill_relevance"] = relevance_score

    if relevance_score < 50:
        insights.append("Skills are mentioned too few times. Increase repetition naturally in experience bullets.")

    # 4️⃣ Readability (sentence length heuristic)
    sentences = re.split(r'[.!?]', resume_text)
    avg_len = sum(len(s.split()) for s in sentences if s.strip()) / max(len(sentences), 1)

    if avg_len <= 20:
        readability = 85
    elif avg_len <= 30:
        readability = 70
    else:
        readability = 50

    scores["readability"] = readability

    if readability < 60:
        insights.append("Long sentences detected. Shorter bullet points improve ATS parsing.")

    # 5️⃣ Overall ATS Score
    overall = round(
        (keyword_score * 0.35) +
        (section_score * 0.2) +
        (relevance_score * 0.25) +
        (readability * 0.2),
        2
    )

    scores["overall"] = overall

    return scores, insights

