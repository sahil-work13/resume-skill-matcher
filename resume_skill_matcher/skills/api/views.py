from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from skills.models import Skill
from .serializers import SkillSerializer


class SkillSearchAPIView(APIView):
    """
    Search skills by canonical name or alias
    Example:
      /api/skills/search/?q=python
    """

    def get(self, request):
        query = request.GET.get("q", "").lower()

        if not query:
            return Response([], status=status.HTTP_200_OK)

        skills = Skill.objects.filter(
            canonical_name__icontains=query
        ) | Skill.objects.filter(
            aliases__icontains=query
        )

        serializer = SkillSerializer(skills.distinct(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SkillNormalizeAPIView(APIView):
    """
    Normalize raw skill text into canonical skill
    Input:
      { "text": "python3" }
    Output:
      { "canonical_skill": "python" }
    """

    def post(self, request):
        raw_text = request.data.get("text", "").lower().strip()

        if not raw_text:
            return Response(
                {"error": "text field required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Exact canonical match
        skill = Skill.objects.filter(canonical_name=raw_text).first()
        if skill:
            return Response({"canonical_skill": skill.canonical_name})

        # 2. Alias match
        for s in Skill.objects.all():
            if raw_text in s.aliases:
                return Response({"canonical_skill": s.canonical_name})

        # 3. Not found
        return Response(
            {"canonical_skill": None},
            status=status.HTTP_200_OK,
        )
