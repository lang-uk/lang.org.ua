# Generated by Django 4.1.4 on 2022-12-21 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0007_genericsitesettings"),
    ]

    operations = [
        migrations.AddField(
            model_name="genericsitesettings",
            name="ga_account",
            field=models.CharField(default="", max_length=30),
        ),
    ]