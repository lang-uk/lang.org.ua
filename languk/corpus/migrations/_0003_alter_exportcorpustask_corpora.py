# Generated by Django 3.2.4 on 2021-08-18 13:01

import corpus.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0002_auto_20210818_1454'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exportcorpustask',
            name='corpora',
            field=corpus.models.ChoiceArrayField(base_field=models.CharField(choices=[('news', 'News and magazines'), ('wiki', 'Ukrainian Wikipedia'), ('fiction', 'Fiction'), ('court', 'Sampled court decisions'), ('laws', 'Laws and bylaws')], max_length=10), size=None),
        ),
    ]
