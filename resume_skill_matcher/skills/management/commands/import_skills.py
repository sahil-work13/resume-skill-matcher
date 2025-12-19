import csv
from django.core.management.base import BaseCommand
from skills.models import Skill


class Command(BaseCommand):
    help = "Import skills from CSV file (ESCO / O*NET / custom)"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)
        parser.add_argument("--source", type=str, default="Manual")

    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        source = options["source"]

        created_count = 0
        updated_count = 0

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                canonical_name = row["skill"].strip()
                aliases_raw = row.get("aliases", "")
                category = row.get("category", "General")

                # Normalize aliases
                aliases = [
                    a.strip().lower()
                    for a in aliases_raw.split("|")
                    if a.strip()
                ]

                skill, created = Skill.objects.get_or_create(
                    canonical_name=canonical_name.lower(),
                    defaults={
                        "aliases": aliases,
                        "category": category,
                        "source": source,
                    },
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1
                    # Optional: update aliases if missing
                    if not skill.aliases:
                        skill.aliases = aliases
                        skill.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Import complete → Created: {created_count}, Updated: {updated_count}"
            )
        )
