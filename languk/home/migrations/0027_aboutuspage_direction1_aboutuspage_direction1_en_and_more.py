# Generated by Django 4.1.8 on 2024-03-22 13:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0026_aboutuspage"),
    ]

    operations = [
        migrations.AddField(
            model_name="aboutuspage",
            name="direction1",
            field=models.TextField(default="", verbose_name="[UA] Перший напрямок"),
        ),
        migrations.AddField(
            model_name="aboutuspage",
            name="direction1_en",
            field=models.TextField(default="", verbose_name="[EN] Перший напрямок"),
        ),
        migrations.AddField(
            model_name="aboutuspage",
            name="direction2",
            field=models.TextField(default="", verbose_name="[UA] Другий напрямок"),
        ),
        migrations.AddField(
            model_name="aboutuspage",
            name="direction2_en",
            field=models.TextField(default="", verbose_name="[EN] Другий напрямок"),
        ),
        migrations.AddField(
            model_name="aboutuspage",
            name="direction3",
            field=models.TextField(default="", verbose_name="[UA] Третій напрямок"),
        ),
        migrations.AddField(
            model_name="aboutuspage",
            name="direction3_en",
            field=models.TextField(default="", verbose_name="[EN] Третій напрямок"),
        ),
        migrations.AddField(
            model_name="aboutuspage",
            name="directions_title",
            field=models.TextField(
                default="", verbose_name="[UA] Розділ Напрямки Роботи (заголовок)"
            ),
        ),
        migrations.AddField(
            model_name="aboutuspage",
            name="directions_title_en",
            field=models.TextField(
                default="", verbose_name="[EN] Розділ Напрямки Роботи (заголовок)"
            ),
        ),
        migrations.AddField(
            model_name="aboutuspage",
            name="team",
            field=models.TextField(
                default="", verbose_name="[UA] Розділ Наша Команда (заголовок)"
            ),
        ),
        migrations.AddField(
            model_name="aboutuspage",
            name="team_en",
            field=models.TextField(
                default="", verbose_name="[EN] Розділ Наша Команда (заголовок)"
            ),
        ),
    ]
