"""Catalog use cases: homepage cards and badge, products index, section
accordions (expand, list/cards toggle, hover affordance), artifact page
(content, styled table, copy-to-clipboard, info panel), pagination."""
import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.django_db


def test_homepage_section_cards_badge_and_ctas(visit, page, site_tree):
    visit("/uk/")

    cards = page.locator(".card.card__home")
    expect(cards).to_have_count(3)
    expect(cards.filter(has_text="Корпуси")).to_be_visible()

    # the korpusi section holds a recently updated artifact -> badge
    expect(
        cards.filter(has_text="Корпуси").locator(".star-text")
    ).to_have_text("Нові надходження")
    expect(cards.filter(has_text="Моделі").locator(".star-text")).to_have_count(0)

    # CTA buttons wired to the public form pages
    expect(
        page.locator("a", has_text="Доповнити продукт").first
    ).to_have_attribute("href", "/uk/submit-product/")
    expect(
        page.locator("a", has_text="Залишити відгук").first
    ).to_have_attribute("href", "/uk/usage-feedback/")


def test_products_index_lists_sections(visit, page, site_tree):
    visit("/uk/produkty/")

    expect(page.locator(".products .h1")).to_have_text("Продукти")
    expect(page.locator(".card.card__home")).to_have_count(3)
    with page.expect_navigation():
        page.locator(".card.card__home", has_text="Корпуси").click()
    assert page.url.endswith("/uk/produkty/korpusi/")


def test_section_accordion_first_open_and_expand_second(visit, page, site_tree):
    visit("/uk/produkty/korpusi/")

    items = page.locator(".service.accordion")
    expect(items).to_have_count(3)

    # first item is open (data-open), its body and info panel visible
    first = items.first
    assert "active" in (first.get_attribute("class") or "")
    expect(first.locator(".service-info")).to_be_visible()
    expect(first.locator(".info-block__download").first).to_be_visible()

    # collapsed second item expands on head click
    second = items.nth(1)
    assert "active" not in (second.get_attribute("class") or "")
    second.locator(".service-head").click()
    expect(second.locator(".service-body")).to_be_visible()
    page.wait_for_function(
        "el => el.classList.contains('active')", arg=second.element_handle()
    )


def test_section_accordion_head_is_clickable_affordance(visit, page, site_tree):
    visit("/uk/produkty/korpusi/")

    head = page.locator(".service.accordion").nth(1).locator(".service-head")
    assert head.evaluate("el => getComputedStyle(el).cursor") == "pointer"

    title = head.locator(".service-head__title")
    before = title.evaluate("el => getComputedStyle(el).color")
    head.hover()
    page.wait_for_function(
        f"el => getComputedStyle(el).color !== '{before}'",
        arg=title.element_handle(),
    )


def test_section_cards_list_toggle(visit, page, site_tree):
    visit("/uk/produkty/korpusi/")

    services_list = page.locator(".services-list")
    assert "cards" not in (services_list.get_attribute("class") or "")

    page.locator(".services-types .button-fill", has_text="Картки").click()
    page.wait_for_function(
        "el => el.classList.contains('cards')", arg=services_list.element_handle()
    )
    page.locator(".services-types .button-fill", has_text="Список").click()
    page.wait_for_function(
        "el => !el.classList.contains('cards')", arg=services_list.element_handle()
    )


def test_artifact_page_content_table_and_info_panel(visit, page, site_tree):
    visit("/uk/produkty/korpusi/test-corpus/")

    expect(page.locator(".h1", has_text="Тестовий корпус")).to_be_visible()

    # rich-text table is wrapped and styled by catalog.css
    table = page.locator(".service-content .table table")
    expect(table).to_be_visible()
    assert table.evaluate(
        "el => getComputedStyle(el.querySelector('td')).borderTopWidth"
    ) == "1px"

    # info panel: license, stats, typed links with captions
    info = page.locator(".service-info")
    expect(info).to_be_visible()
    expect(info).to_contain_text("CC BY-SA 4.0")
    expect(info).to_contain_text("100M токенів")
    expect(info.locator(".info-block__download", has_text="Код")).to_have_attribute(
        "href", "https://github.com/lang-uk/test-corpus"
    )


def test_artifact_page_copy_code_to_clipboard(visit, page, context, site_tree):
    context.grant_permissions(["clipboard-read", "clipboard-write"])
    visit("/uk/produkty/korpusi/test-corpus/")

    copy_block = page.locator(".copy")
    expect(copy_block.locator(".copy__text")).to_contain_text("pip install test-corpus")
    copy_block.locator(".copy__button").click()
    assert (
        page.evaluate("() => navigator.clipboard.readText()").strip()
        == "pip install test-corpus"
    )


def test_section_pagination(visit, page, site_tree, monkeypatch):
    from catalog.models import SectionPage

    monkeypatch.setattr(SectionPage, "ARTIFACTS_PER_PAGE", 2)
    visit("/uk/produkty/korpusi/")

    expect(page.locator(".service.accordion")).to_have_count(2)
    pagination = page.locator(".pagination")
    expect(pagination).to_be_visible()
    with page.expect_navigation():
        pagination.locator("a", has_text="2").click()
    assert "page=2" in page.url
    expect(page.locator(".service.accordion")).to_have_count(1)
