from django.contrib import admin
from .models import Resume
from .models import MatchAnalytics


admin.site.register(Resume)
@admin.register(MatchAnalytics)
class MatchAnalyticsAdmin(admin.ModelAdmin):
    list_display = ("user", "score", "semantic_score", "created_at")
    list_filter = ("created_at",)