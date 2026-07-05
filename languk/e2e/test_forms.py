"""Public form use cases: submit-a-product, usage feedback, and contact —
happy paths end-to-end (browser -> POST -> moderation inbox -> thank-you
page -> editor notification) plus server-side validation errors.

The reCAPTCHA v3 widget needs network access to google.com; the e2e settings
use Google's universal test keys so any minted token passes verification.
"""
import pytest
from playwright.sync_api import expect

pytestmark = pytest.mark.django_db


def choose(page, option_text):
    """Pick an option in the nice-select2-skinned dropdown (the native
    select is hidden, so drive the widget like a user would)."""
    page.locator(".nice-select").first.click()
    page.locator(".nice-select .option", has_text=option_text).click()


def test_submit_product_happy_path(visit, page, site_tree):
    visit("/uk/submit-product/")

    choose(page, "Датасети")
    page.fill("input[name=name]", "Новий датасет")
    page.fill("textarea[name=description]", "Опис нового датасету")
    page.fill("textarea[name=links]", "https://github.com/lang-uk/new-dataset")
    page.fill("input[name=license]", "MIT")
    page.fill("input[name=submitter_name]", "Тестер")
    page.fill("input[name=submitter_email]", "tester@example.com")
    with page.expect_navigation():
        page.click(".add-product-form button[type=submit]")

    expect(page.locator(".contact__submitted")).to_contain_text("Дякуємо!")

    from catalog.models import ArtifactSubmission

    submission = ArtifactSubmission.objects.get()
    assert submission.name == "Новий датасет"
    assert submission.artifact_type.slug == "datasets"
    assert not submission.processed

    from django.core import mail

    assert any("Новий датасет" in m.subject for m in mail.outbox)


def test_submit_product_validation_errors_rendered(visit, page, site_tree):
    visit("/uk/submit-product/")

    # required fields carry native browser validation...
    assert page.get_attribute("input[name=name]", "required") is not None
    # ...bypass it to exercise the server-side error rendering
    page.eval_on_selector(".add-product-form form", "f => f.noValidate = true")
    with page.expect_navigation():
        page.click(".add-product-form button[type=submit]")

    expect(page.locator(".form-row.error").first).to_be_visible()
    expect(page.locator(".error-message").first).to_be_visible()

    from catalog.models import ArtifactSubmission

    assert ArtifactSubmission.objects.count() == 0


def test_usage_feedback_happy_path(visit, page, site_tree):
    visit("/uk/usage-feedback/")

    choose(page, "Тестовий корпус")
    page.fill("textarea[name=how_used]", "Використовуємо в дослідженнях")
    page.fill("input[name=organization]", "Тестова організація")
    page.fill("input[name=submitter_name]", "Тестер")
    page.fill("input[name=submitter_email]", "tester@example.com")
    with page.expect_navigation():
        page.click(".add-product-form button[type=submit]")

    expect(page.locator(".contact__submitted")).to_contain_text("Дякуємо!")

    from catalog.models import UsageFeedback

    feedback = UsageFeedback.objects.get()
    assert feedback.artifact.slug == "test-corpus"
    assert feedback.organization == "Тестова організація"


def test_contact_form_happy_path(visit, page, site_tree):
    visit("/uk/contacts/")

    page.fill("input[name=author]", "Тестер")
    page.fill("input[name=email]", "tester@example.com")
    page.fill("textarea[name=text]", "Тестове повідомлення")
    with page.expect_navigation():
        page.click(".contact__form button[type=submit]")

    expect(page.locator(".contact__submitted")).to_contain_text("Дякуємо!")

    from home.models import ContactUsMessage

    message = ContactUsMessage.objects.get()
    assert message.author == "Тестер"


def test_header_cta_leads_to_submit_form(visit, page, site_tree):
    visit("/uk/")
    with page.expect_navigation():
        page.locator("header a", has_text="Доповнити продукт").click()
    assert page.url.endswith("/uk/submit-product/")
    expect(page.locator(".add-product-form form")).to_be_visible()
