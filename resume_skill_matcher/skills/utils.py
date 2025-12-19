import re
from difflib import SequenceMatcher
from skills.models import Skill

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return text


def fuzzy_match(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def extract_skills_from_text(text: str, threshold=0.85):
    text = normalize_text(text)
    found = set()

    skills = Skill.objects.all()

    for skill in skills:
        candidates = [skill.canonical_name]
        if skill.aliases:
            candidates += skill.aliases.split("|")

        for candidate in candidates:
            candidate = candidate.strip()
            if candidate in text:
                found.add(skill.canonical_name)
            elif fuzzy_match(candidate, text) >= threshold:
                found.add(skill.canonical_name)

    return sorted(found)
