# Generated by Django 3.2.4 on 2021-10-05 20:47

import corpus.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0003_alter_exportcorpustask_corpora'),
    ]

    operations = [
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
