# Generated by Django 4.1.4 on 2023-03-16 17:29

import corpus.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("corpus", "0011_alter_buildfreqvocabtask_filtering_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="buildfreqvocabtask",
            name="corpora",
            field=corpus.models.ChoiceArrayField(
                base_field=models.CharField(
                    choices=[
                        ("news", "News and magazines"),
                        ("wikipedia", "Ukrainian Wikipedia"),
                        ("fiction", "Fiction"),
                        ("court", "Sampled court decisions"),
                        ("laws", "Laws and bylaws"),
                        ("forum", "Forums"),
                        ("social", "Social media and telegram"),
                    ],
                    max_length=10,
                ),
                size=None,
            ),
        ),
        migrations.AlterField(
            model_name="exportcorpustask",
            name="corpora",
            field=corpus.models.ChoiceArrayField(
                base_field=models.CharField(
                    choices=[
                        ("news", "News and magazines"),
                        ("wikipedia", "Ukrainian Wikipedia"),
                        ("fiction", "Fiction"),
                        ("court", "Sampled court decisions"),
                        ("laws", "Laws and bylaws"),
                        ("forum", "Forums"),
                        ("social", "Social media and telegram"),
                    ],
                    max_length=10,
                ),
                size=None,
            ),
        ),
        migrations.AlterField(
            model_name="tagwithudpipetask",
            name="corpora",
            field=corpus.models.ChoiceArrayField(
                base_field=models.CharField(
                    choices=[
                        ("news", "News and magazines"),
                        ("wikipedia", "Ukrainian Wikipedia"),
                        ("fiction", "Fiction"),
                        ("court", "Sampled court decisions"),
                        ("laws", "Laws and bylaws"),
                        ("forum", "Forums"),
                        ("social", "Social media and telegram"),
                    ],
                    max_length=10,
                ),
                size=None,
            ),
        ),
        migrations.CreateModel(
            name="ProcessWithNlpUKTask",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                        verbose_name="id",
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        blank=True, max_length=256, verbose_name="description"
                    ),
                ),
                (
                    "created_on",
                    models.DateTimeField(auto_now_add=True, verbose_name="created on"),
                ),
                (
                    "started_on",
                    models.DateTimeField(null=True, verbose_name="started on"),
                ),
                (
                    "completed_on",
                    models.DateTimeField(null=True, verbose_name="completed on"),
                ),
                (
                    "progress",
                    models.IntegerField(blank=True, null=True, verbose_name="progress"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("PENDING", "PENDING"),
                            ("RECEIVED", "RECEIVED"),
                            ("STARTED", "STARTED"),
                            ("PROGESS", "PROGESS"),
                            ("SUCCESS", "SUCCESS"),
                            ("FAILURE", "FAILURE"),
                            ("REVOKED", "REVOKED"),
                            ("REJECTED", "REJECTED"),
                            ("RETRY", "RETRY"),
                            ("IGNORED", "IGNORED"),
                        ],
                        db_index=True,
                        default="PENDING",
                        max_length=128,
                        verbose_name="status",
                    ),
                ),
                (
                    "job_id",
                    models.CharField(blank=True, max_length=128, verbose_name="job id"),
                ),
                (
                    "mode",
                    models.CharField(
                        choices=[
                            ("UNKNOWN", "UNKNOWN"),
                            ("SYNC", "SYNC"),
                            ("ASYNC", "ASYNC"),
                        ],
                        db_index=True,
                        default="UNKNOWN",
                        max_length=128,
                        verbose_name="mode",
                    ),
                ),
                (
                    "failure_reason",
                    models.CharField(
                        blank=True, max_length=256, verbose_name="failure reason"
                    ),
                ),
                ("log_text", models.TextField(blank=True, verbose_name="log text")),
                (
                    "corpora",
                    corpus.models.ChoiceArrayField(
                        base_field=models.CharField(
                            choices=[
                                ("news", "News and magazines"),
                                ("wikipedia", "Ukrainian Wikipedia"),
                                ("fiction", "Fiction"),
                                ("court", "Sampled court decisions"),
                                ("laws", "Laws and bylaws"),
                                ("forum", "Forums"),
                                ("social", "Social media and telegram"),
                            ],
                            max_length=10,
                        ),
                        size=None,
                    ),
                ),
                (
                    "force",
                    models.BooleanField(
                        default=False,
                        verbose_name="Process all texts, including already processed",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-created_on",),
                "get_latest_by": "created_on",
                "abstract": False,
            },
        ),
    ]
