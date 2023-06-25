# Generated by Django 4.1.8 on 2023-06-25 16:42

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailimages", "0025_alter_image_file_alter_rendition_file"),
        ("home", "0019_homepage_become_a_part_cta_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepage",
            name="media_title",
            field=models.TextField(
                default="", verbose_name="[UA] Стань частиною (заклик)"
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="media_title_en",
            field=models.TextField(
                default="", verbose_name="[EN] Стань частиною (заклик)"
            ),
        ),
        migrations.CreateModel(
            name="PressArticles",
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
                    "source",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Назва джерела"
                    ),
                ),
                (
                    "source_en",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="[EN] Назва джерела"
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="Назва публікації"
                    ),
                ),
                (
                    "title_en",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="[EN] Назва публікації"
                    ),
                ),
                (
                    "date_of_publish",
                    models.DateField(blank=True, verbose_name="Дата публікації"),
                ),
                (
                    "link_external",
                    models.URLField(
                        blank=True, verbose_name="Посилання на текст або матеріал"
                    ),
                ),
                (
                    "media_logo",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                        verbose_name="Логотип автору матеріалу",
                    ),
                ),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="press_articles",
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