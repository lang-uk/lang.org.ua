# Generated by Django 3.2.12 on 2022-12-19 15:42

import corpus.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0009_auto_20220628_1859'),
    ]

    operations = [
        migrations.AlterField(
            model_name='buildfreqvocabtask',
            name='filtering',
            field=corpus.models.ChoiceArrayField(base_field=models.CharField(choices=[('rus', 'Filter out texts where russian word > ukrainian'), ('rus_gcld', "Filter out texts where gcld says it's ukrainian"), ('short', 'Filter out texts, where title and body combined are too short')], max_length=10), blank=True, default=list, size=None),
        ),
        migrations.AlterField(
            model_name='exportcorpustask',
            name='filtering',
            field=corpus.models.ChoiceArrayField(base_field=models.CharField(choices=[('rus', 'Filter out texts where russian word > ukrainian'), ('rus_gcld', "Filter out texts where gcld says it's ukrainian"), ('short', 'Filter out texts, where title and body combined are too short')], max_length=10), blank=True, size=None),
        ),
        migrations.AlterField(
            model_name='exportcorpustask',
            name='processing',
            field=models.CharField(choices=[('orig', 'Original texts in markdown format'), ('orig_titles', 'Original titles'), ('text_only', 'Titles & texts with markdown stripped'), ('tokens', 'Tokenized by NLP-UK lib'), ('lemmas', 'Lemmatized by NLP-UK lib')], max_length=15),
        ),
    ]
