# Generated by Django 4.1.8 on 2023-06-25 18:07

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0023_rename_pressarticles_pressarticle"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="pressarticle",
            options={"ordering": ("-date_of_publish",)},
        ),
    ]
