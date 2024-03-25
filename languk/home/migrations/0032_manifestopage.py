# Generated by Django 4.1.8 on 2024-03-24 00:25

from django.db import migrations, models
import django.db.models.deletion
import wagtail.fields


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailcore", "0089_log_entry_data_json_null_to_object"),
        ("home", "0031_founder_twitter_volunteer_twitter"),
    ]

    operations = [
        migrations.CreateModel(
            name="ManifestoPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "title_en",
                    models.CharField(
                        default="", max_length=255, verbose_name="[EN] Назва сторінки"
                    ),
                ),
                (
                    "global_class",
                    models.CharField(
                        blank=True,
                        default="",
                        max_length=255,
                        verbose_name="CSS-Клас сторінки",
                    ),
                ),
                (
                    "body",
                    wagtail.fields.RichTextField(
                        default="", verbose_name="[UA] Загальний текст сторінки"
                    ),
                ),
                (
                    "body_en",
                    wagtail.fields.RichTextField(
                        default="", verbose_name="[EN] Загальний текст сторінки"
                    ),
                ),
                (
                    "svg_image",
                    models.TextField(
                        blank=True,
                        default="",
                        help_text="Content of the SVG tag, ignored if empty",
                        verbose_name="SVG image icon (raw text) to display next to menu item",
                    ),
                ),
                (
                    "explainer",
                    wagtail.fields.RichTextField(
                        default="", verbose_name="[UA] Текст маніфесту"
                    ),
                ),
                (
                    "explainer_en",
                    wagtail.fields.RichTextField(
                        default="", verbose_name="[EN] Текст маніфесту"
                    ),
                ),
                (
                    "thesis1_title",
                    models.TextField(
                        default="", verbose_name="[UA] Теза 1 (заголовок)"
                    ),
                ),
                (
                    "thesis1_title_en",
                    models.TextField(
                        default="", verbose_name="[EN] Теза 1 (заголовок)"
                    ),
                ),
                (
                    "thesis1_description",
                    models.TextField(default="", verbose_name="[UA] Теза 1 (опис)"),
                ),
                (
                    "thesis1_description_en",
                    models.TextField(default="", verbose_name="[EN] Теза 1 (опис)"),
                ),
                (
                    "thesis2_title",
                    models.TextField(
                        default="", verbose_name="[UA] Теза 2 (заголовок)"
                    ),
                ),
                (
                    "thesis2_title_en",
                    models.TextField(
                        default="", verbose_name="[EN] Теза 2 (заголовок)"
                    ),
                ),
                (
                    "thesis2_description",
                    models.TextField(default="", verbose_name="[UA] Теза 2 (опис)"),
                ),
                (
                    "thesis2_description_en",
                    models.TextField(default="", verbose_name="[EN] Теза 2 (опис)"),
                ),
                (
                    "thesis3_title",
                    models.TextField(
                        default="", verbose_name="[UA] Теза 3 (заголовок)"
                    ),
                ),
                (
                    "thesis3_title_en",
                    models.TextField(
                        default="", verbose_name="[EN] Теза 3 (заголовок)"
                    ),
                ),
                (
                    "thesis3_description",
                    models.TextField(default="", verbose_name="[UA] Теза 3 (опис)"),
                ),
                (
                    "thesis3_description_en",
                    models.TextField(default="", verbose_name="[EN] Теза 3 (опис)"),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=("wagtailcore.page",),
        ),
    ]
