# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-02 00:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import wagtail.wagtailcore.fields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0029_unicode_slugfield_dj19'),
        ('home', '0005_auto_20160924_0127'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaticPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('title_en', models.CharField(default='', max_length=255, verbose_name='[EN] Назва сторінки')),
                ('global_class', models.CharField(blank=True, default='', max_length=255, verbose_name='CSS-Клас сторінки')),
                ('body', wagtail.wagtailcore.fields.RichTextField(default='', verbose_name='[UA] Загальний текст сторінки')),
                ('body_en', wagtail.wagtailcore.fields.RichTextField(default='', verbose_name='[EN] Загальний текст сторінки')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]
