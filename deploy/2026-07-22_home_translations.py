# One-shot content update, 2026-07-22 (part 2): the EN homepage rendered in
# Ukrainian because several *_en fields contained copy-pasted Ukrainian text
# rather than translations. Replaces those with English, fixes the
# half-translated ProductsPage intro, and two leftovers in artifact bodies.
# Ukrainian *examples* inside English artifact bodies are left alone on
# purpose. Idempotent: each fix fires only while the field still holds the
# known Ukrainian text.
#
# Run locally:   python manage.py shell < deploy/2026-07-22_home_translations.py
# Run on prod:   docker exec -i $(docker-compose ps -q app) \
#                    python manage.py shell < 2026-07-22_home_translations.py

import re

from catalog.models import ArtifactPage
from home.models import EndUser, HomePage, ProductsPage

CYR = re.compile(r"[а-яіїєґА-ЯІЇЄҐ]")
updated = []

home = HomePage.objects.first()
changed = False
for field, value in {
    "slogan_title_en": "a community of Ukrainian NLP professionals",
    "slogan_text_en": (
        '<p data-block-key="x7ejq">Supporting existing and developing new '
        "projects to collect Ukrainian corpora and other text data. The core "
        "of the community are activists, volunteers and other participants "
        "who share our principles.</p>"
    ),
    "aboutus_title_en": "About us",
    "aboutus_text_en": (
        '<p data-block-key="ts0tu">Lang-uk is an open community of '
        "specialists in computational text processing (developers, linguists, "
        "researchers), built on shared principles, that maintains existing "
        "and develops new projects for collecting Ukrainian corpora and "
        "other text data.</p>"
    ),
}.items():
    if CYR.search(str(getattr(home, field) or "")):
        setattr(home, field, value)
        changed = True
if str(home.title_en or "").strip() in ("", "Homepage"):
    home.title_en = "Ukrainian NLP community"
    changed = True
if changed:
    home.save()
    updated.append(home)

for eu in EndUser.objects.all():
    if CYR.search(str(eu.role_use_en or "")):
        eu.role_use_en = "As a source for writing articles"
        eu.save()
        if home not in updated:
            updated.append(home)  # orderable child of the homepage

products = ProductsPage.objects.first()
if products is not None and CYR.search(str(products.intro_en or "")):
    products.intro_en = (
        '<p data-block-key="6i8sf">At the moment, all results of our work '
        'are hosted on <a href="https://github.com/lang-uk/new_design">'
        "<b>github</b></a> in the organization's repositories</p>"
    )
    products.save()
    updated.append(products)

we = ArtifactPage.objects.filter(slug="word-embeddings-word2vec-glove-lexvec").first()
if we is not None:
    # \s also matches the non-breaking space that hid this line from the
    # first translation pass
    body_en = re.sub(
        r"Параметри GloVe для\sмалих корпусів \(художня література\):",
        "GloVe parameters for small corpora (fiction):",
        str(we.body_en),
    )
    if body_en != str(we.body_en):
        we.body_en = body_en
        we.save()
        updated.append(we)

ut = ArtifactPage.objects.filter(slug="ubertext-corpus").first()
if ut is not None:
    body_en = str(ut.body_en).replace(">Корпус<", ">Corpus<")
    if body_en != str(ut.body_en):
        ut.body_en = body_en
        ut.save()
        updated.append(ut)

for page in updated:
    page = page.specific_class.objects.get(pk=page.pk)
    revision = page.save_revision()
    if page.live:
        revision.publish()

print("updated + republished:", len(updated), sorted(p.slug for p in updated))
