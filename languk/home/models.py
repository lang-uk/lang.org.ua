from django.db import models
from django.utils import translation
from django.conf import settings

from wagtail.core import hooks
from wagtail.core.models import Page, Orderable
from modelcluster.fields import ParentalKey
from wagtail.core.fields import RichTextField
from wagtail.core.whitelist import attribute_rule, allow_without_attributes
from wagtail.admin.edit_handlers import InlinePanel, FieldPanel, PageChooserPanel

from wagtailmenus.models import AbstractMainMenuItem

from wagtail.contrib.settings.models import (
    BaseGenericSetting,
    register_setting,
)


@register_setting
class GenericSiteSettings(BaseGenericSetting):
    github = models.URLField()
    telegram = models.URLField()
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    copyright = models.CharField(max_length=120)
    ga_account = models.CharField(max_length=30, default="")


@hooks.register("construct_whitelister_element_rules")
def whitelister_element_rules():
    return {
        "u": allow_without_attributes,
        "table": attribute_rule({"cellspacing": True, "cellpadding": True, "border": True}),
        "td": attribute_rule({"valign": True, "style": True}),
        "tr": allow_without_attributes,
        "th": allow_without_attributes,
        "tbody": allow_without_attributes,
        "tfoot": allow_without_attributes,
        "thead": allow_without_attributes,
        "p": attribute_rule({"align": True}),
    }


class TranslatedField(object):
    def __init__(self, ua_field, en_field):
        self.ua_field = ua_field
        self.en_field = en_field

    def __get__(self, instance, owner):
        if translation.get_language() == "en":
            return getattr(instance, self.en_field) or getattr(instance, self.ua_field)
        else:
            return getattr(instance, self.ua_field)


class LinkFields(models.Model):
    caption = models.CharField(max_length=255, blank=True, verbose_name="Заголовок")
    caption_en = models.CharField(max_length=255, blank=True, verbose_name="[EN] Заголовок")

    translated_caption = TranslatedField(
        "caption",
        "caption_en",
    )

    link_external = models.URLField("Зовнішнє посилання", blank=True)
    link_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.CASCADE,
        verbose_name="Або посилання на існуючу сторінку",
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        else:
            return self.link_external

    panels = [
        FieldPanel("caption"),
        FieldPanel("caption_en"),
        FieldPanel("link_external"),
        PageChooserPanel("link_page"),
    ]

    class Meta:
        abstract = True


class AbstractPage(Page):
    title_en = models.CharField(default="", max_length=255, verbose_name="[EN] Назва сторінки")

    global_class = models.CharField(default="", max_length=255, blank=True, verbose_name="CSS-Клас сторінки")

    body = RichTextField(default="", verbose_name="[UA] Загальний текст сторінки")

    body_en = RichTextField(default="", verbose_name="[EN] Загальний текст сторінки")

    svg_image = models.TextField(
        verbose_name="SVG image icon (raw text) to display next to menu item",
        default="",
        blank=True,
        help_text="Content of the SVG tag, ignored if empty",
    )

    translated_title = TranslatedField(
        "title",
        "title_en",
    )

    translated_body = TranslatedField(
        "body",
        "body_en",
    )

    content_panels = [
        FieldPanel("title", classname="full title"),
        FieldPanel("title_en", classname="full title"),
        FieldPanel("body", classname="full"),
        FieldPanel("body_en", classname="full"),
        FieldPanel("svg_image", classname="full"),
        FieldPanel("global_class", classname="full"),
    ]

    def get_sitemap_urls(self, request=None):
        for code, _ in settings.LANGUAGES:
            translation.activate(code)

            yield {"location": self.get_full_url(request), "lastmod": self.latest_revision_created_at}

            translation.deactivate()

    class Meta:
        abstract = True


class StaticPage(AbstractPage):
    template = "home/static_page.html"


class HomePage(AbstractPage):
    template = "home/home_page.html"

    slogan_title = models.TextField(default="", verbose_name="[UA] Слоган (заголовок)")
    slogan_title_en = models.TextField(default="", verbose_name="[EN] Слоган (заголовок)")
    translated_slogan_title = TranslatedField(
        "slogan_title",
        "slogan_title_en",
    )

    slogan_text = RichTextField(default="", verbose_name="[UA] Слоган (текст)")
    slogan_text_en = RichTextField(default="", verbose_name="[EN] Слоган (текст)")
    translated_slogan_text = TranslatedField(
        "slogan_text",
        "slogan_text_en",
    )

    aboutus_title = models.TextField(default="", verbose_name="[UA] Про нас (заголовок)")
    aboutus_title_en = models.TextField(default="", verbose_name="[EN] Про нас (заголовок)")
    translated_aboutus_title = TranslatedField(
        "aboutus_title",
        "aboutus_title_en",
    )

    aboutus_text = RichTextField(default="", verbose_name="[UA] Про нас (текст)")
    aboutus_text_en = RichTextField(default="", verbose_name="[EN] Про нас (текст)")
    translated_aboutus_text = TranslatedField(
        "aboutus_text",
        "aboutus_text_en",
    )

    content_panels = [
        FieldPanel("title", classname="full title"),
        FieldPanel("title_en", classname="full title"),

        FieldPanel("slogan_title"),
        FieldPanel("slogan_title_en"),
        FieldPanel("slogan_text", classname="full"),
        FieldPanel("slogan_text_en", classname="full"),

        FieldPanel("aboutus_title"),
        FieldPanel("aboutus_title_en"),
        FieldPanel("aboutus_text", classname="full"),
        FieldPanel("aboutus_text_en", classname="full"),

        FieldPanel("body", classname="full"),
        FieldPanel("body_en", classname="full"),
        FieldPanel("global_class", classname="full"),
    ]


class ProductsPage(AbstractPage):
    template = "home/products_page.html"

    content_panels = [
        FieldPanel("title", classname="full title"),
        FieldPanel("title_en", classname="full title"),
        FieldPanel("body", classname="full"),
        FieldPanel("body_en", classname="full"),
        FieldPanel("svg_image", classname="full"),
        FieldPanel("global_class", classname="full"),
    ]


class ProductPage(AbstractPage):
    template = "home/product_page.html"


class LangUkMainMenuItem(AbstractMainMenuItem):
    """A custom menu item model to be used by ``wagtailmenus.MainMenu``"""

    menu = ParentalKey(
        "wagtailmenus.MainMenu",
        on_delete=models.CASCADE,
        related_name="lang_uk_menu_items",  # See the base.py's WAGTAILMENUS_MAIN_MENU_ITEMS_RELATED_NAME
    )

    show_in_footer = models.BooleanField(
        verbose_name="Show menu item in the footer menu",
        default=True,
        help_text="Display this item in the site footer",
    )

    # Also override the panels attribute, so that the new fields appear
    # in the admin interface
    panels = (
        PageChooserPanel("link_page"),
        FieldPanel("link_url"),
        FieldPanel("url_append"),
        FieldPanel("link_text"),
        FieldPanel("show_in_footer"),
        FieldPanel("allow_subnav"),
    )
