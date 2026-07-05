from django.db import migrations


def populate_community_artifacts(apps, schema_editor):
    """Create draft catalog entries for the curated public lang-uk projects
    from GitHub and Hugging Face (see catalog/community_artifacts.py).

    Page-tree creation needs real Wagtail model behaviour (treebeard paths,
    revisions), so this deliberately uses the live models via the shared
    helper instead of historical apps.get_model() models. The operation is
    idempotent and skips gracefully: entries whose section pages don't exist
    yet (e.g. before convert_product_pages ran on production) are left out —
    re-run later with `manage.py import_community_artifacts`.
    """
    from catalog.community_artifacts import populate

    populate()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0004_feedbackpage_submitartifactpage_usagefeedback_and_more"),
    ]

    operations = [
        migrations.RunPython(populate_community_artifacts, migrations.RunPython.noop),
    ]
