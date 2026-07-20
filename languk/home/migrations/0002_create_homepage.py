# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_homepage(apps, schema_editor):
    from django.conf import settings

    # Get models
    ContentType = apps.get_model('contenttypes.ContentType')
    Page = apps.get_model('wagtailcore.Page')
    Site = apps.get_model('wagtailcore.Site')
    HomePage = apps.get_model('home.HomePage')
    Locale = apps.get_model('wagtailcore.Locale')

    # Delete the default homepage
    Page.objects.filter(id=2).delete()

    # Create content type for homepage model
    homepage_content_type, created = ContentType.objects.get_or_create(
        model='homepage', app_label='home')

    # On a fresh database this runs after Wagtail's locale migrations, so
    # pages must carry a locale (historical installs are unaffected)
    locale, _ = Locale.objects.get_or_create(
        language_code=settings.LANGUAGE_CODE
    )

    # Create a new homepage
    homepage = HomePage.objects.create(
        title="Homepage",
        slug='home',
        content_type=homepage_content_type,
        path='00010001',
        depth=2,
        numchild=0,
        url_path='/home/',
        locale=locale,
    )

    # Create a site with the new homepage set as the root
    Site.objects.create(
        hostname='localhost', root_page=homepage, is_default_site=True)


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_homepage),
    ]
