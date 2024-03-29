# Generated by Django 3.2.4 on 2021-10-05 20:52

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
        migrations.AlterField(
            model_name='exportcorpustask',
            name='file_compression',
            field=models.CharField(choices=[('none', 'No compression'), ('bz2', 'Bzip2'), ('lzma', 'LZMA')], default='none', max_length=5),
        ),
        migrations.AlterField(
            model_name='exportcorpustask',
            name='filtering',
            field=corpus.models.ChoiceArrayField(base_field=models.CharField(choices=[('rus', 'Filter out texts with a lot of russian words'), ('short', 'Filter out texts, where title and body combined are too short')], max_length=10), blank=True, size=None),
        ),
    ]
