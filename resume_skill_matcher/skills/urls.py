from django.urls import path
from skills.api_views import skill_search, normalize_skills

urlpatterns = [
    path("search/", skill_search),
    path("normalize/", normalize_skills),
]
