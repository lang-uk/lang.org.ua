# Generated by Django 4.1.8 on 2023-06-25 15:44

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0017_homepage_useful_text_homepage_useful_text_en_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="homepage",
            name="useful_text",
        ),
        migrations.RemoveField(
            model_name="homepage",
            name="useful_text_en",
        ),
        migrations.CreateModel(
            name="EndUser",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                (
                    "role_name",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Назва ролі"
                    ),
                ),
                (
                    "role_name_en",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="[EN] Назва ролі"
                    ),
                ),
                (
                    "role_use",
                    models.CharField(
                        blank=True, max_length=1024, verbose_name="Опис ролі"
                    ),
                ),
                (
                    "role_use_en",
                    models.CharField(
                        blank=True, max_length=1024, verbose_name="[EN] Опис ролі"
                    ),
                ),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="end_users",
                        to="home.homepage",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
    ]