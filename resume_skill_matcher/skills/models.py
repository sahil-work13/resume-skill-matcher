from django.db import models


class Skill(models.Model):
    """
    Canonical skill representation.
    Example:
      canonical_name = "python"
      aliases = ["python3", "py", "cpython"]
    """

    canonical_name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Primary normalized skill name (lowercase)"
    )

    aliases = models.JSONField(
        default=list,
        blank=True,
        help_text="List of alternative names / synonyms"
    )

    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Skill category (AI, Backend, Cloud, etc.)"
    )

    source = models.CharField(
        max_length=50,
        default="manual",
        help_text="ESCO / O*NET / Manual"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["canonical_name"]

    def __str__(self):
        return self.canonical_name
