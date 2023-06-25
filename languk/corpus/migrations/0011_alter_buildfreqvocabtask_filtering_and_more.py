# Generated by Django 4.1.4 on 2023-01-04 20:13

import corpus.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("corpus", "0010_auto_20221219_1742"),
    ]

    operations = [
        migrations.AlterField(
            model_name="buildfreqvocabtask",
            name="filtering",
            field=corpus.models.ChoiceArrayField(
                base_field=models.CharField(
                    choices=[
                        ("rus", "Filter out texts where russian word > ukrainian"),
                        (
                            "rus_gcld",
                            "Filter out texts where gcld says it's NOT ukrainian",
                        ),
                        (
                            "short",
                            "Filter out texts, where title and body combined are too short",
                        ),
                    ],
                    max_length=10,
                ),
                blank=True,
                default=list,
                size=None,
            ),
        ),
        migrations.AlterField(
            model_name="exportcorpustask",
            name="file_format",
            field=models.CharField(
                choices=[("txt", "Text File"), ("jsonl", "JSONLines File")],
                default="txt",
                max_length=5,
            ),
        ),
        migrations.AlterField(
            model_name="exportcorpustask",
            name="filtering",
            field=corpus.models.ChoiceArrayField(
                base_field=models.CharField(
                    choices=[
                        ("rus", "Filter out texts where russian word > ukrainian"),
                        (
                            "rus_gcld",
                            "Filter out texts where gcld says it's NOT ukrainian",
                        ),
                        (
                            "short",
                            "Filter out texts, where title and body combined are too short",
                        ),
                    ],
                    max_length=10,
                ),
                blank=True,
                size=None,
            ),
        ),
    ]