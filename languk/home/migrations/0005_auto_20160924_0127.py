# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-23 22:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_homepage_global_class'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homepage',
            name='global_class',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='CSS-Клас сторінки'),
        ),
    ]
