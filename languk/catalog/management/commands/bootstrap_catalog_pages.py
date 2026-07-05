from django.core.management.base import BaseCommand

from catalog.models import ArtifactType, FeedbackPage, SectionPage, SubmitArtifactPage
from home.models import HomePage, ProductsPage


class Command(BaseCommand):
    help = (
        "Create the catalog pages the redesign needs and that no data "
        "migration owns: the Датасети section plus the submit-a-product and "
        "usage-feedback form pages. Idempotent: existing pages are left "
        "untouched. Run after convert_product_pages."
    )

    def _publish(self, parent, page):
        parent.add_child(instance=page)
        page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"created {page.slug} ({page.url})"))

    def handle(self, *args, **options):
        home = HomePage.objects.live().first()
        products = ProductsPage.objects.live().first()
        if home is None or products is None:
            self.stderr.write("HomePage/ProductsPage not found — nothing to do")
            return

        if not SectionPage.objects.filter(artifact_type__slug="datasets").exists():
            self._publish(
                products,
                SectionPage(
                    title="Датасети",
                    title_en="Datasets",
                    slug="datasety",
                    artifact_type=ArtifactType.objects.get(slug="datasets"),
                ),
            )
        else:
            self.stdout.write("datasets section exists — skipping")

        if not SubmitArtifactPage.objects.exists():
            self._publish(
                home,
                SubmitArtifactPage(
                    title="Доповнити продукт",
                    title_en="Submit a product",
                    slug="submit-product",
                    body="<p>Поділіться своїм продуктом зі спільнотою lang-uk.</p>",
                    body_en="<p>Share your product with the lang-uk community.</p>",
                    thank_you_caption="<p>Дякуємо!</p>",
                    thank_you_caption_en="<p>Thank you!</p>",
                    thank_you_text="<p>Ми розглянемо вашу заявку найближчим часом.</p>",
                    thank_you_text_en="<p>We will review your submission shortly.</p>",
                ),
            )
        else:
            self.stdout.write("submit page exists — skipping")

        if not FeedbackPage.objects.exists():
            self._publish(
                home,
                FeedbackPage(
                    title="Відгук про використання",
                    title_en="Usage feedback",
                    slug="usage-feedback",
                    body="<p>Розкажіть, як і де ви використовуєте продукти lang-uk.</p>",
                    body_en="<p>Tell us how and where you use lang-uk products.</p>",
                    thank_you_caption="<p>Дякуємо!</p>",
                    thank_you_caption_en="<p>Thank you!</p>",
                    thank_you_text="<p>Ваш відгук дуже важливий для нас.</p>",
                    thank_you_text_en="<p>Your feedback matters a lot to us.</p>",
                ),
            )
        else:
            self.stdout.write("feedback page exists — skipping")
