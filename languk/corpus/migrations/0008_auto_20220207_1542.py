# Generated by Django 3.2.12 on 2022-02-07 13:42

import corpus.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0007_buildfreqvocabtask'),
    ]

    operations = [
        migrations.AddField(
            model_name='buildfreqvocabtask',
            name='file_compression',
            field=models.CharField(choices=[('none', 'No compression'), ('bz2', 'Bzip2'), ('lzma', 'LZMA')], default='none', max_length=5),
        ),
        migrations.AddField(
            model_name='buildfreqvocabtask',
            name='file_format',
            field=models.CharField(choices=[('csv', 'CSV file')], default='csv', max_length=5),
        ),
        migrations.AddField(
            model_name='buildfreqvocabtask',
            name='filtering',
            field=corpus.models.ChoiceArrayField(base_field=models.CharField(choices=[('rus', 'Filter out texts with a lot of russian words'), ('short', 'Filter out texts, where title and body combined are too short')], max_length=10), blank=True, default=[], size=None),
        ),
    ]
