"""Site-wide use cases: search from the header, search results with
snippets, language switching, custom 404, and both locales rendering."""
import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.django_db


def test_search_from_header(visit, page, site_tree):
    visit("/uk/")

    form = page.locator("header .search-form").first
    form.locator("input[name=query]").fill("корпус")
    with page.expect_navigation():
        form.locator("input[name=query]").press("Enter")

    assert "/uk/search/" in page.url and "query=" in page.url
    results = page.locator(".search-result__item")
    expect(results.first).to_be_visible()
    expect(results.filter(has_text="Тестовий корпус").first).to_be_visible()
    # snippet text under the title
    expect(
        results.filter(has_text="Тестовий корпус").first.locator("p.text-m")
    ).to_contain_text("тестовий корпус", ignore_case=True)


def test_search_result_navigates_to_artifact(visit, page, site_tree):
    visit("/uk/search/?query=корпус")
    with page.expect_navigation():
        page.locator(".search-result__item a.h4", has_text="Тестовий корпус").click()
    assert page.url.endswith("/uk/produkty/korpusi/test-corpus/")


def test_language_switcher_on_wagtail_page(visit, page, site_tree):
    visit("/uk/produkty/korpusi/")
    # the alternate-language link only shows when the widget is hovered
    page.locator("header .navigation-action__item.lang").hover()
    with page.expect_navigation():
        page.locator("header .lang__item.lang-en").click()
    assert "/en/" in page.url
    expect(page.locator(".services .h1")).to_have_text("Corpora")


def test_english_locale_renders_catalog(visit, page, site_tree):
    visit("/en/produkty/korpusi/test-corpus/")
    expect(page.locator(".h1", has_text="Test corpus")).to_be_visible()


def test_custom_404_page(visit, page, site_tree):
    response = page.request.get(f"{visit.base_url}/uk/no-such-page/")
    assert response.status == 404

    visit("/uk/no-such-page/")
    expect(page.locator(".article__content", has_text="404")).to_be_visible()
    expect(page.locator("img[alt='404']")).to_be_visible()


def test_footer_renders_site_settings(visit, page, site_tree):
    visit("/uk/")
    footer = page.locator("footer, .footer").first
    expect(footer).to_contain_text("info@lang.org.ua")
