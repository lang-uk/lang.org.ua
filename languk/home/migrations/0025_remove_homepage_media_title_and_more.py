# Generated by Django 4.1.8 on 2023-06-25 18:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0024_alter_pressarticle_options"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="homepage",
            name="media_title",
        ),
        migrations.RemoveField(
            model_name="homepage",
            name="media_title_en",
        ),
    ]
