import os

# The Playwright sync API drives the browser from a greenlet, which Django's
# async-unsafe guard would otherwise reject when fixtures touch the ORM.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

from datetime import date

import pytest


@pytest.fixture
def site_tree(db):
    """A minimal but complete published page tree covering every use case:
    home, products index, three catalog sections with artifacts (one with a
    recent update for the badge, one with table/code/links in the body),
    both public forms and the contact page.

    Self-sufficient: rebuilds the baseline rows (locale, root page, artifact
    types) because the transactional flush between live-server tests wipes
    migration-seeded data."""
    from django.conf import settings
    from django.contrib.contenttypes.models import ContentType
    from wagtail.models import Locale, Page, Site
    from wagtailmenus.models import MainMenu

    from catalog.models import ArtifactType, SectionPage, SubmitArtifactPage, FeedbackPage
    from catalog.utils import create_artifact_draft
    from home.models import ContactUsPage, GenericSiteSettings, HomePage, ProductsPage

    locale, _ = Locale.objects.get_or_create(language_code=settings.LANGUAGE_CODE)

    for order, (slug, name, name_en) in enumerate(
        [
            ("corpora", "Корпуси", "Corpora"),
            ("models", "Моделі", "Models"),
            ("datasets", "Датасети", "Datasets"),
        ]
    ):
        ArtifactType.objects.get_or_create(
            slug=slug, defaults={"name": name, "name_en": name_en, "sort_order": order}
        )

    root = Page.objects.filter(depth=1).first()
    if root is None:
        root = Page.add_root(
            title="Root",
            slug="root",
            locale=locale,
            content_type=ContentType.objects.get_for_model(Page),
        )
    else:
        # own the tree: drop any pre-existing homepage (queryset delete
        # bypasses treebeard, so fix the child counter)
        Page.objects.filter(depth__gte=2).delete()
        Page.objects.filter(depth=1).update(numchild=0)
        root.refresh_from_db()

    home = HomePage(
        title="Головна",
        title_en="Home",
        slug="home",
        slogan_title="Lang-uk — спільнота фахівців з українського NLP",
        slogan_title_en="Lang-uk — Ukrainian NLP community",
        slogan_text="<p>Підтримка та розвиток українського NLP.</p>",
        slogan_text_en="<p>Supporting Ukrainian NLP.</p>",
        aboutus_title="Про нас",
        aboutus_title_en="About us",
        aboutus_text="<p>Тестовий опис спільноти.</p>",
        aboutus_text_en="<p>Test community description.</p>",
        partners_title="Наші партнери",
        partners_title_en="Our partners",
        useful_title="Кому це корисно",
        useful_title_en="Who finds it useful",
    )
    root.add_child(instance=home)
    home.save_revision().publish()

    # deleting the old homepage cascades to its Site record
    site, _ = Site.objects.update_or_create(
        is_default_site=True,
        defaults={"hostname": "localhost", "port": 80, "root_page": home},
    )
    MainMenu.objects.get_or_create(site=site)
    GenericSiteSettings.objects.create(
        github="https://github.com/lang-uk",
        telegram="https://t.me/lang_uk",
        email="info@lang.org.ua",
        phone="+380000000000",
        copyright="lang-uk",
        notification_emails="editors@example.com",
    )

    products = ProductsPage(
        title="Продукти",
        title_en="Products",
        slug="produkty",
        intro="<p>Всі результати нашої роботи.</p>",
        intro_en="<p>All our results.</p>",
    )
    home.add_child(instance=products)
    products.save_revision().publish()

    sections = {}
    for slug, type_slug, title, title_en in [
        ("korpusi", "corpora", "Корпуси", "Corpora"),
        ("modeli", "models", "Моделі", "Models"),
        ("datasety", "datasets", "Датасети", "Datasets"),
    ]:
        section = SectionPage(
            title=title,
            title_en=title_en,
            slug=slug,
            artifact_type=ArtifactType.objects.get(slug=type_slug),
        )
        products.add_child(instance=section)
        section.save_revision().publish()
        sections[slug] = section

    artifacts = {}
    artifacts["rich"] = create_artifact_draft(
        sections["korpusi"],
        title="Тестовий корпус",
        title_en="Test corpus",
        slug_source="test-corpus",
        artifact_type=sections["korpusi"].artifact_type,
        short_description="Великий тестовий корпус українських текстів.",
        body=(
            "<p>Опис тестового корпусу.</p>"
            "<pre>pip install test-corpus</pre>"
            "<table><thead><tr><th>Розмір</th><th>Токени</th></tr></thead>"
            "<tbody><tr><td>1GB</td><td>100M</td></tr></tbody></table>"
        ),
        authors="lang-uk",
        license="CC BY-SA 4.0",
        stats="100M токенів",
        last_significant_update=date.today(),
        links=[
            ("github", "https://github.com/lang-uk/test-corpus", "Код"),
            ("download", "https://lang.org.ua/static/test.bz2", "Завантажити"),
        ],
        publish=True,
    )
    artifacts["second"] = create_artifact_draft(
        sections["korpusi"],
        title="Другий корпус",
        title_en="Second corpus",
        slug_source="second-corpus",
        artifact_type=sections["korpusi"].artifact_type,
        short_description="Ще один корпус.",
        body="<p>Другий тестовий корпус.</p>",
        links=[("github", "https://github.com/lang-uk/second", "")],
        publish=True,
    )
    artifacts["third"] = create_artifact_draft(
        sections["korpusi"],
        title="Третій корпус",
        title_en="Third corpus",
        slug_source="third-corpus",
        artifact_type=sections["korpusi"].artifact_type,
        short_description="І ще один.",
        body="<p>Третій тестовий корпус.</p>",
        publish=True,
    )
    artifacts["model"] = create_artifact_draft(
        sections["modeli"],
        title="Тестова модель",
        title_en="Test model",
        slug_source="test-model",
        artifact_type=sections["modeli"].artifact_type,
        short_description="Модель без нових оновлень.",
        body="<p>Опис моделі.</p>",
        publish=True,
    )

    submit_page = SubmitArtifactPage(
        title="Доповнити продукт",
        title_en="Submit a product",
        slug="submit-product",
        body="<p>Поділіться своїм продуктом.</p>",
        thank_you_caption="<p>Дякуємо!</p>",
        thank_you_text="<p>Ми розглянемо вашу заявку.</p>",
    )
    home.add_child(instance=submit_page)
    submit_page.save_revision().publish()

    feedback_page = FeedbackPage(
        title="Відгук про використання",
        title_en="Usage feedback",
        slug="usage-feedback",
        body="<p>Розкажіть, як ви використовуєте продукти.</p>",
        thank_you_caption="<p>Дякуємо!</p>",
        thank_you_text="<p>Ваш відгук важливий.</p>",
    )
    home.add_child(instance=feedback_page)
    feedback_page.save_revision().publish()

    contact_page = ContactUsPage(
        title="Контакти",
        title_en="Contacts",
        slug="contacts",
        body="<p>Напишіть нам.</p>",
        thank_you_caption="<p>Дякуємо!</p>",
        thank_you_text="<p>Відповімо найближчим часом.</p>",
    )
    home.add_child(instance=contact_page)
    contact_page.save_revision().publish()

    return {
        "home": home,
        "products": products,
        "sections": sections,
        "artifacts": artifacts,
        "submit_page": submit_page,
        "feedback_page": feedback_page,
        "contact_page": contact_page,
    }


@pytest.fixture
def visit(page, context, live_server, site_tree):
    """Navigate helper bound to the live server; pre-dismisses the cookie
    banner so it never intercepts clicks."""
    context.add_cookies(
        [
            {
                "name": "show_cookies_block",
                "value": "no",
                "url": live_server.url,
            }
        ]
    )

    def _visit(path):
        page.goto(f"{live_server.url}{path}")
        return page

    _visit.base_url = live_server.url
    return _visit
