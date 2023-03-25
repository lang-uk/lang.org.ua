# Generated by Django 4.1.4 on 2023-01-04 20:13

from django.db import migrations, models
import django.db.models.deletion
import modelcluster.fields
import wagtailmenus.models.menuitems


class Migration(migrations.Migration):

    dependencies = [
        ("wagtailmenus", "0023_remove_use_specific"),
        ("wagtailcore", "0078_referenceindex"),
        ("home", "0008_genericsitesettings_ga_account"),
    ]

    operations = [
        migrations.CreateModel(
            name="LangUkMainMenuItem",
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
                    "link_url",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="link to a custom URL",
                    ),
                ),
                (
                    "url_append",
                    models.CharField(
                        blank=True,
                        help_text="Use this to optionally append a #hash or querystring to the above page's URL.",
                        max_length=255,
                        verbose_name="append to URL",
                    ),
                ),
                (
                    "handle",
                    models.CharField(
                        blank=True,
                        help_text="Use this field to optionally specify an additional value for each menu item, which you can then reference in custom menu templates.",
                        max_length=100,
                        verbose_name="handle",
                    ),
                ),
                (
                    "link_text",
                    models.CharField(
                        blank=True,
                        help_text="Provide the text to use for a custom URL, or set on an internal page link to use instead of the page's title.",
                        max_length=255,
                        verbose_name="link text",
                    ),
                ),
                (
                    "allow_subnav",
                    models.BooleanField(
                        default=True,
                        help_text="NOTE: The sub-menu might not be displayed, even if checked. It depends on how the menu is used in this project's templates.",
                        verbose_name="allow sub-menu for this item",
                    ),
                ),
                (
                    "show_in_footer",
                    models.BooleanField(
                        default=True,
                        help_text="Do not display this item in the site footer",
                        verbose_name="Show menu item in the footer menu",
                    ),
                ),
                (
                    "link_page",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="wagtailcore.page",
                        verbose_name="link to an internal page",
                    ),
                ),
                (
                    "menu",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lang_uk_menu_items",
                        to="wagtailmenus.mainmenu",
                    ),
                ),
            ],
            options={
                "verbose_name": "menu item",
                "verbose_name_plural": "menu items",
                "ordering": ("sort_order",),
                "abstract": False,
            },
            bases=(models.Model, wagtailmenus.models.menuitems.MenuItem),
        ),
    ]
