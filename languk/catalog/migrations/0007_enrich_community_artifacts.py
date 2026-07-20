from django.db import migrations


def enrich_community_artifacts(apps, schema_editor):
    """Backfill authors, licenses and paper links (harvested from the GitHub
    API, the Hugging Face API and the ACL Anthology) onto the community
    artifact pages created by the 0005 migration.

    Uses the live models via the shared helper for the same reason as 0005
    (revisions need real Wagtail behaviour). Idempotent and additive: blank
    fields are filled, existing values are left alone, and only links with
    new URLs are appended. On a fresh database where the pages don't exist
    yet this is a no-op — import_community_artifacts later creates the pages
    from the already-enriched data.
    """
    from catalog.community_artifacts import enrich

    enrich()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0006_alter_feedbackpage_thank_you_caption_and_more"),
    ]

    operations = [
        migrations.RunPython(enrich_community_artifacts, migrations.RunPython.noop),
    ]
