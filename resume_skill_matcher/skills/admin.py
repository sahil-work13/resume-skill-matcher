from django.contrib import admin
from .models import Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("canonical_name", "category", "source")
    search_fields = ("canonical_name",)
