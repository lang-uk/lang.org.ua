from datetime import date, timedelta

from django.core.paginator import Paginator
from django.db import models
from django.utils.translation import gettext_lazy as _

from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import TaggedItemBase

from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from home.models import AbstractPage, FormPageMixin, TranslatedField

# Artifacts updated within this window get the "Нові надходження" badge
NEW_BADGE_DAYS = 90


@register_snippet
class ArtifactType(models.Model):
    """Kind of catalog artifact (corpora, dictionaries, models, datasets, ...).

    Types are data, not code: new kinds are added in the Wagtail admin.
    """

    name = models.CharField(max_length=255, verbose_name="Назва типу")
    name_en = models.CharField(max_length=255, verbose_name="[EN] Назва типу")

    translated_name = TranslatedField(
        "name",
        "name_en",
    )

    slug = models.SlugField(unique=True, verbose_name="Слаг")

    svg_image = models.TextField(
        verbose_name="SVG image icon (raw text)",
        default="",
        blank=True,
        help_text="Content of the SVG tag, ignored if empty",
    )

    sort_order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортування")

    panels = [
        FieldPanel("name"),
        FieldPanel("name_en"),
        FieldPanel("slug"),
        FieldPanel("svg_image"),
        FieldPanel("sort_order"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ("sort_order", "name")
        verbose_name = "Тип продукту"
        verbose_name_plural = "Типи продуктів"


class ArtifactPageTag(TaggedItemBase):
    content_object = ParentalKey(
        "catalog.ArtifactPage", on_delete=models.CASCADE, related_name="tagged_items"
    )


class ArtifactLink(Orderable):
    KIND_CHOICES = [
        ("github", "GitHub"),
        ("huggingface", "Hugging Face"),
        ("paper", "Наукова праця"),
        ("demo", "Демо"),
        ("download", "Завантаження"),
        ("docs", "Документація"),
        ("other", "Інше"),
    ]

    page = ParentalKey(
        "catalog.ArtifactPage", on_delete=models.CASCADE, related_name="links"
    )

    kind = models.CharField(
        max_length=20,
        choices=KIND_CHOICES,
        default="download",
        verbose_name="Тип посилання",
    )
    url = models.URLField(verbose_name="Посилання")

    caption = models.CharField(
        max_length=255, blank=True, default="", verbose_name="Підпис (опційно)"
    )
    caption_en = models.CharField(
        max_length=255, blank=True, default="", verbose_name="[EN] Підпис (опційно)"
    )

    translated_caption = TranslatedField(
        "caption",
        "caption_en",
    )

    panels = [
        FieldPanel("kind"),
        FieldPanel("url"),
        FieldPanel("caption"),
        FieldPanel("caption_en"),
    ]

    def __str__(self):
        return f"{self.get_kind_display()}: {self.url}"


class ArtifactPage(AbstractPage):
    """A single catalog artifact: corpus, dataset, model, library, service, ..."""

    template = "catalog/artifact_page.html"
    parent_page_types = ["catalog.SectionPage"]
    subpage_types = []

    artifact_type = models.ForeignKey(
        ArtifactType,
        on_delete=models.PROTECT,
        related_name="artifacts",
        verbose_name="Тип продукту",
    )

    short_description = models.TextField(
        default="", blank=True, verbose_name="Короткий опис (для картки)"
    )
    short_description_en = models.TextField(
        default="", blank=True, verbose_name="[EN] Короткий опис (для картки)"
    )

    translated_short_description = TranslatedField(
        "short_description",
        "short_description_en",
    )

    authors = models.CharField(
        max_length=512, blank=True, default="", verbose_name="Автори"
    )
    license = models.CharField(
        max_length=255, blank=True, default="", verbose_name="Ліцензія"
    )
    stats = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Обсяг/статистика (вільний текст)",
    )

    last_significant_update = models.DateField(
        null=True, blank=True, verbose_name="Дата останнього суттєвого оновлення"
    )

    thumbnail = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Мініатюра",
    )

    tags = ClusterTaggableManager(through=ArtifactPageTag, blank=True)

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["extra_css_files"] = ["css/catalog.css"]
        return context

    @property
    def has_recent_updates(self):
        if not self.last_significant_update:
            return False
        return self.last_significant_update >= date.today() - timedelta(
            days=NEW_BADGE_DAYS
        )

    search_fields = Page.search_fields + [
        index.SearchField("title_en"),
        index.SearchField("body"),
        index.SearchField("body_en"),
        index.SearchField("short_description"),
        index.SearchField("short_description_en"),
        index.SearchField("authors"),
        index.FilterField("artifact_type_id"),
    ]

    content_panels = [
        FieldPanel("title", classname="full title"),
        FieldPanel("title_en", classname="full title"),
        FieldPanel("artifact_type"),
        FieldPanel("short_description"),
        FieldPanel("short_description_en"),
        FieldPanel("body", classname="full"),
        FieldPanel("body_en", classname="full"),
        InlinePanel("links", label="Посилання"),
        FieldPanel("authors"),
        FieldPanel("license"),
        FieldPanel("stats"),
        FieldPanel("last_significant_update"),
        FieldPanel("thumbnail"),
        FieldPanel("tags"),
        FieldPanel("svg_image", classname="full"),
        FieldPanel("global_class", classname="full"),
    ]

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукти"


class SectionPage(AbstractPage):
    """A catalog section listing artifacts of one type (corpora, models, ...)."""

    template = "catalog/section_page.html"
    parent_page_types = ["home.ProductsPage"]
    subpage_types = ["catalog.ArtifactPage"]

    ARTIFACTS_PER_PAGE = 24

    artifact_type = models.ForeignKey(
        ArtifactType,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="sections",
        verbose_name="Тип продукту",
    )

    content_panels = AbstractPage.content_panels + [
        FieldPanel("artifact_type"),
    ]

    def get_artifacts(self):
        return (
            ArtifactPage.objects.child_of(self)
            .live()
            .prefetch_related("links", "tagged_items__tag")
            .order_by(
                models.F("last_significant_update").desc(nulls_last=True), "title"
            )
        )

    @property
    def has_recent_updates(self):
        cutoff = date.today() - timedelta(days=NEW_BADGE_DAYS)
        return (
            ArtifactPage.objects.child_of(self)
            .live()
            .filter(last_significant_update__gte=cutoff)
            .exists()
        )

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        paginator = Paginator(self.get_artifacts(), self.ARTIFACTS_PER_PAGE)
        context["artifacts"] = paginator.get_page(request.GET.get("page"))
        context["extra_css_files"] = ["css/catalog.css"]
        return context

    class Meta:
        verbose_name = "Розділ каталогу"
        verbose_name_plural = "Розділи каталогу"


class ArtifactSubmission(models.Model):
    """A community-submitted artifact awaiting moderation."""

    artifact_type = models.ForeignKey(
        ArtifactType,
        on_delete=models.PROTECT,
        related_name="submissions",
        verbose_name=_("Тип продукту"),
    )
    name = models.CharField(_("Назва продукту"), max_length=255)
    description = models.TextField(_("Опис"))
    links = models.TextField(
        _("Посилання"), blank=True, help_text=_("По одному посиланню в рядку")
    )
    license = models.CharField(_("Ліцензія"), max_length=255, blank=True)
    authors = models.CharField(_("Автори"), max_length=512, blank=True)
    submitter_name = models.CharField(_("Ваше ім'я"), max_length=255)
    submitter_email = models.EmailField(_("Ваш e-mail"))
    added = models.DateTimeField(_("Був надісланий"), auto_now_add=True)
    processed = models.BooleanField(_("Опрацьовано"), default=False)

    class Meta:
        ordering = ("-added",)
        verbose_name = _("Заявка на додавання продукту")
        verbose_name_plural = _("Заявки на додавання продуктів")

    def __str__(self):
        return f"{self.name} ({self.artifact_type}) від {self.submitter_name}"


class UsageFeedback(models.Model):
    """Community feedback on how and where the products are used."""

    artifact = models.ForeignKey(
        ArtifactPage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="feedback",
        verbose_name=_("Продукт"),
    )
    product_name = models.CharField(
        _("Продукт (як текст)"),
        max_length=255,
        blank=True,
        help_text=_("Якщо продукту немає у списку"),
    )
    how_used = models.TextField(_("Як і де використовується"))
    organization = models.CharField(_("Організація/проєкт"), max_length=255, blank=True)
    submitter_name = models.CharField(_("Ваше ім'я"), max_length=255)
    submitter_email = models.EmailField(_("Ваш e-mail"))
    added = models.DateTimeField(_("Був надісланий"), auto_now_add=True)

    class Meta:
        ordering = ("-added",)
        verbose_name = _("Відгук про використання")
        verbose_name_plural = _("Відгуки про використання")

    def __str__(self):
        product = self.artifact or self.product_name
        return f"{product}: {self.submitter_name} <{self.submitter_email}>"


class SubmitArtifactPage(FormPageMixin, AbstractPage):
    """Public form: propose a new artifact for the catalog."""

    template = "catalog/form_page.html"
    parent_page_types = ["home.HomePage"]
    subpage_types = []

    content_panels = AbstractPage.content_panels + FormPageMixin.thank_you_panels

    submit_label = _("Надіслати продукт")

    def get_form_class(self):
        from catalog.forms import SubmitArtifactForm

        return SubmitArtifactForm

    def get_notification_subject(self, obj):
        return f"lang.org.ua: нова заявка на продукт «{obj.name}»"

    def get_notification_body(self, obj):
        return (
            f"Тип: {obj.artifact_type}\n"
            f"Назва: {obj.name}\n"
            f"Автори: {obj.authors}\n"
            f"Ліцензія: {obj.license}\n"
            f"Посилання:\n{obj.links}\n\n"
            f"{obj.description}\n\n"
            f"Від: {obj.submitter_name} <{obj.submitter_email}>"
        )

    class Meta:
        verbose_name = "Сторінка додавання продукту"


class FeedbackPage(FormPageMixin, AbstractPage):
    """Public form: how and where are the products used."""

    template = "catalog/form_page.html"
    parent_page_types = ["home.HomePage"]
    subpage_types = []

    content_panels = AbstractPage.content_panels + FormPageMixin.thank_you_panels

    submit_label = _("Надіслати відгук")

    def get_form_class(self):
        from catalog.forms import UsageFeedbackForm

        return UsageFeedbackForm

    def get_notification_subject(self, obj):
        return "lang.org.ua: новий відгук про використання продуктів"

    def get_notification_body(self, obj):
        return (
            f"Продукт: {obj.artifact or obj.product_name}\n"
            f"Організація: {obj.organization}\n\n"
            f"{obj.how_used}\n\n"
            f"Від: {obj.submitter_name} <{obj.submitter_email}>"
        )

    class Meta:
        verbose_name = "Сторінка відгуків про використання"
