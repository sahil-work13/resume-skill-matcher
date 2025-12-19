from django.urls import path
from .views import SkillSearchAPIView, SkillNormalizeAPIView

urlpatterns = [
    path("search/", SkillSearchAPIView.as_view(), name="skill-search"),
    path("normalize/", SkillNormalizeAPIView.as_view(), name="skill-normalize"),
]
