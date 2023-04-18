# Generated by Django 4.1.4 on 2023-04-18 15:23

import corpus.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("corpus", "0012_alter_buildfreqvocabtask_corpora_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="buildfreqvocabtask",
            name="filtering",
            field=corpus.models.ChoiceArrayField(
                base_field=models.CharField(
                    choices=[
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
            name="filtering",
            field=corpus.models.ChoiceArrayField(
                base_field=models.CharField(
                    choices=[
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
        migrations.AlterField(
            model_name="exportcorpustask",
            name="processing",
            field=models.CharField(
                choices=[
                    ("orig", "Original texts in markdown format"),
                    ("orig_titles", "Original titles"),
                    ("text_only", "Titles & texts with markdown stripped"),
                    ("tokens", "Tokenized by NLP-UK lib"),
                    ("tokens_wo_punct", "Tokenized by NLP-UK lib without punctuation"),
                    ("sentences", "Sentence-split by NLP-UK lib"),
                    ("lemmas", "Lemmatized by NLP-UK lib"),
                ],
                max_length=15,
            ),
        ),
    ]
