"""Corpus browser use cases. The UberText browser reads from MongoDB, which
the test harness does not provision — these run only against an already
populated server:

    E2E_BASE_URL=http://127.0.0.1:8000 pytest e2e/test_corpus_live.py
"""
import os

import pytest
from playwright.sync_api import expect

BASE_URL = os.environ.get("E2E_BASE_URL")

pytestmark = pytest.mark.skipif(
    not BASE_URL, reason="corpus e2e needs a populated server (set E2E_BASE_URL)"
)


@pytest.fixture
def corpus(page):
    def _visit(path):
        page.goto(f"{BASE_URL}{path}")
        return page

    return _visit


def test_corpus_home_tables(corpus, page):
    corpus("/corpus/")
    expect(page.locator(".article .h1")).to_contain_text("UberText")
    expect(page.locator(".table table").first).to_be_visible()


def test_corpus_source_chart(corpus, page):
    corpus("/corpus/")
    with page.expect_navigation():
        page.locator(".table a[href^='/corpus/']").first.click()

    expect(page.locator(".table table")).to_be_visible()
    if page.locator("#source_timeline").count():
        # self-hosted Chartist rendered an SVG timeline
        expect(page.locator("#source_timeline svg")).to_be_visible()


def test_corpus_reading_view_is_bare(corpus, page):
    corpus("/corpus/")
    source_link = page.locator(".table a[href^='/corpus/']").first.get_attribute("href")
    corpus(source_link)
    sample_link = page.locator("a[href*='/sample/']").first
    if not sample_link.count():
        pytest.skip("source has no samples")
    with page.expect_navigation():
        sample_link.click()

    with page.expect_navigation():
        page.locator(".excerpt a[href^='/corpus/']", has_text="Повна версія").first.click()

    # distraction-free reading view: new design assets, no site header
    assert page.locator("header.header").count() == 0
    expect(page.locator(".corpus-text")).to_be_visible()
