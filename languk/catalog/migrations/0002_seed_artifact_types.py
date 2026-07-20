from django.db import migrations

LAUNCH_TYPES = [
    # (slug, name UA, name EN, sort_order)
    ("corpora", "Корпуси", "Corpora", 10),
    ("dictionaries", "Словники", "Dictionaries", 20),
    ("gazetteers", "Газетири", "Gazetteers", 30),
    ("services", "Сервіси", "Services", 40),
    ("libraries", "Бібліотеки", "Libraries", 50),
    ("models", "Моделі", "Models", 60),
    ("datasets", "Датасети", "Datasets", 70),
]


def seed_types(apps, schema_editor):
    ArtifactType = apps.get_model("catalog", "ArtifactType")
    for slug, name, name_en, sort_order in LAUNCH_TYPES:
        ArtifactType.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "name_en": name_en, "sort_order": sort_order},
        )


def unseed_types(apps, schema_editor):
    ArtifactType = apps.get_model("catalog", "ArtifactType")
    ArtifactType.objects.filter(
        slug__in=[slug for slug, *_ in LAUNCH_TYPES], artifacts__isnull=True
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_types, unseed_types),
    ]
