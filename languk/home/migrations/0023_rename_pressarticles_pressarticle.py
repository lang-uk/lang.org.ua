# Generated by Django 4.1.8 on 2023-06-25 18:06

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("wagtailimages", "0025_alter_image_file_alter_rendition_file"),
        ("home", "0022_alter_pressarticles_options_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="PressArticles",
            new_name="PressArticle",
        ),
    ]