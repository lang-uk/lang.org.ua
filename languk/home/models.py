from django.db import models
from django.utils import translation

from wagtail.wagtailcore.models import Page, Orderable
from modelcluster.fields import ParentalKey
from wagtail.wagtailcore.fields import RichTextField
from wagtail.wagtailadmin.edit_handlers import (
    InlinePanel, FieldPanel, PageChooserPanel)


class TranslatedField(object):
    def __init__(self, ua_field, en_field):
        self.ua_field = ua_field
        self.en_field = en_field

    def __get__(self, instance, owner):
        if translation.get_language() == 'en':
            return (getattr(instance, self.en_field) or
                    getattr(instance, self.ua_field))
        else:
            return getattr(instance, self.ua_field)


class LinkFields(models.Model):
    caption = models.CharField(max_length=255, blank=True,
                               verbose_name="Заголовок")
    caption_en = models.CharField(max_length=255, blank=True,
                                  verbose_name="[EN] Заголовок")

    translated_caption = TranslatedField(
        'caption',
        'caption_en',
    )

    link_external = models.URLField("Зовнішнє посилання", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        verbose_name="Або посилання на існуючу сторінку"
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        else:
            return self.link_external

    panels = [
        FieldPanel('caption'),
        FieldPanel('caption_en'),
        FieldPanel('link_external'),
        PageChooserPanel('link_page')
    ]

    class Meta:
        abstract = True


class HomePageTopMenuLink(Orderable, LinkFields):
    page = ParentalKey('home.HomePage', related_name='top_menu_links')


class HomePage(Page):
    title_en = models.CharField(
        default="", max_length=255,
        verbose_name="[EN] Назва сторінки")

    body = RichTextField(
        default="",
        verbose_name="[UA] Загальний текст сторінки")

    body_en = RichTextField(
        default="",
        verbose_name="[EN] Загальний текст сторінки")

    translated_title = TranslatedField(
        'title',
        'title_en',
    )

    translated_body = TranslatedField(
        'body',
        'body_en',
    )

    content_panels = [
        FieldPanel('title', classname="full title"),
        FieldPanel('title_en', classname="full title"),

        FieldPanel('body', classname="full"),
        FieldPanel('body_en', classname="full"),

        InlinePanel('top_menu_links', label="Меню зверху"),
    ]
