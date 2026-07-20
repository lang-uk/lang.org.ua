from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import connection, transaction

from wagtail.models import Page

from catalog.models import ArtifactType, SectionPage
from home.models import ProductPage


class Command(BaseCommand):
    help = (
        "Convert legacy home.ProductPage sections into catalog.SectionPage in place, "
        "preserving page ids, slugs, URLs and tree position. The ArtifactType is "
        "matched by the page slug unless overridden with --type-map. Note: page "
        "revisions created before the conversion cannot be restored afterwards."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Report what would be converted without touching the database",
        )
        parser.add_argument(
            "--type-map",
            nargs="*",
            default=[],
            metavar="PAGE_SLUG=TYPE_SLUG",
            help="Override the page-slug to artifact-type-slug mapping",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        mapping = dict(pair.split("=", 1) for pair in options["type_map"])
        section_ct = ContentType.objects.get_for_model(SectionPage)
        converted = skipped = 0

        for product_page in ProductPage.objects.all():
            type_slug = mapping.get(product_page.slug, product_page.slug)
            artifact_type = ArtifactType.objects.filter(slug=type_slug).first()
            if artifact_type is None:
                self.stderr.write(
                    f"No ArtifactType with slug '{type_slug}' for page "
                    f"'{product_page.slug}' (#{product_page.pk}) — skipping. "
                    f"Use --type-map {product_page.slug}=<type_slug> to map it."
                )
                skipped += 1
                continue

            self.stdout.write(
                f"Converting '{product_page.slug}' (#{product_page.pk}) → "
                f"SectionPage[{artifact_type.slug}]"
            )
            converted += 1
            if options["dry_run"]:
                continue

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO catalog_sectionpage
                        (page_ptr_id, title_en, global_class, body, body_en,
                         svg_image, artifact_type_id)
                    SELECT page_ptr_id, title_en, global_class, body, body_en,
                           svg_image, %s
                    FROM home_productpage
                    WHERE page_ptr_id = %s
                    """,
                    [artifact_type.pk, product_page.pk],
                )
                cursor.execute(
                    "DELETE FROM home_productpage WHERE page_ptr_id = %s",
                    [product_page.pk],
                )
            Page.objects.filter(pk=product_page.pk).update(content_type=section_ct)

        suffix = " (dry run — no changes made)" if options["dry_run"] else ""
        self.stdout.write(
            self.style.SUCCESS(f"Converted {converted}, skipped {skipped}{suffix}")
        )
