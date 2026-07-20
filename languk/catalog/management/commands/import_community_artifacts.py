from django.core.management.base import BaseCommand

from catalog.community_artifacts import enrich, populate


class Command(BaseCommand):
    help = (
        "Create draft catalog entries for the curated public lang-uk projects "
        "from GitHub and Hugging Face (catalog/community_artifacts.py). "
        "Idempotent: existing slugs are skipped. Use this to re-run the 0005 "
        "data migration after the section pages exist. --enrich additionally "
        "backfills authors/licenses/paper links onto pages that already exist "
        "(blank fields only; re-runs the 0006 data migration)."
    )

    def add_arguments(self, parser):
        parser.add_argument("--publish", action="store_true")
        parser.add_argument("--enrich", action="store_true")

    def handle(self, *args, **options):
        created, skipped = populate(
            publish=options["publish"], log=self.stdout.write
        )
        self.stdout.write(
            self.style.SUCCESS(f"Created {len(created)}, skipped {len(skipped)}")
        )
        if options["enrich"]:
            updated = enrich(log=self.stdout.write)
            self.stdout.write(self.style.SUCCESS(f"Enriched {len(updated)}"))
