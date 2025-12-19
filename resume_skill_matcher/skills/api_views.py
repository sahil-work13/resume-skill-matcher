from rest_framework.decorators import api_view
from rest_framework.response import Response
from skills.models import Skill
from skills.serializers import SkillSerializer
from skills.utils import extract_skills_from_text

@api_view(["GET"])
def skill_search(request):
    q = request.GET.get("q", "")
    skills = Skill.objects.filter(canonical_name__icontains=q)
    return Response(SkillSerializer(skills, many=True).data)


@api_view(["POST"])
def normalize_skills(request):
    text = request.data.get("text", "")
    skills = extract_skills_from_text(text)
    return Response({"skills": skills})
