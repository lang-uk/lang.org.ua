# One-shot content update, 2026-07-22: fill Wagtail promote-tab SEO fields.
# Crafted seo_title + search_description for the structural pages (the home
# page carried literal "Homepage test"/"SEO test" stubs — those are
# replaced), and search_description for every artifact derived from its
# short_description. Artifact titles are already descriptive, so their
# seo_title stays empty (the template appends ": lang-uk" to the title).
#
# Idempotent: fills blanks, replaces only the known stub values.
#
# Run locally:   python manage.py shell < deploy/2026-07-22_seo_meta.py
# Run on prod:   docker exec -i $(docker-compose ps -q app) \
#                    python manage.py shell < 2026-07-22_seo_meta.py

from catalog.models import ArtifactPage
from wagtail.models import Page

STUBS = {"Homepage test", "SEO test", "SEO title"}

META = {
    "home": (
        "Українська обробка природної мови (NLP)",
        "lang-uk — спільнота розробників та дослідників, що створює відкриті "
        "корпуси, датасети, моделі та інструменти для обробки української мови.",
    ),
    "produkty": (
        "Продукти для української NLP",
        "Каталог відкритих продуктів спільноти lang-uk для обробки української "
        "мови: корпуси, словники, газетири, моделі, бібліотеки, сервіси та датасети.",
    ),
    "korpusi": (
        "Корпуси української мови",
        "Відкриті корпуси української мови від lang-uk: UberText 2.0 на 3,3 млрд "
        "токенів, корпус судових рішень, Малюк для тренування LLM та інші.",
    ),
    "slovniki": (
        "Словники української мови",
        "Відкриті електронні словники української мови: наголоси, скорочення, "
        "тональні словники, частотний словник імен та прізвищ, фемінітиви.",
    ),
    "gazetiri": (
        "Газетири та довідкові дані",
        "Газетири й довідкові набори даних для української NLP: імена, "
        "географічні назви та інші структуровані ресурси від lang-uk.",
    ),
    "modeli": (
        "Моделі для української мови",
        "Моделі машинного навчання для української мови: переклад (Драгоман), "
        "NER, POS, ELECTRA, fastText, sentence embeddings, GEC та інші.",
    ),
    "biblioteki": (
        "Бібліотеки для обробки української мови",
        "Відкриті бібліотеки для української NLP: токенізація, наголоси, "
        "фонетична транскрипція, сегментація речень та препроцесинг для TTS.",
    ),
    "servisi": (
        "Сервіси та інструменти української NLP",
        "Онлайн-сервіси та інструменти від lang-uk: мікросервіси токенізації "
        "й NER, лідерборд українських LLM та інші.",
    ),
    "datasety": (
        "Датасети для української мови",
        "Відкриті датасети для машинного навчання українською: NER-розмітка, "
        "виправлення помилок (GEC), бенчмарки ЗНО, рекрутингові дані та інші.",
    ),
    "pro-nas": (
        "Про спільноту lang-uk",
        "Хто ми такі: спільнота розробників, лінгвістів і дослідників, які "
        "будують відкриту інфраструктуру для обробки української мови.",
    ),
    "manifesto": (
        "Маніфест lang-uk",
        "Чому ми це робимо: принципи та цілі ініціативи lang-uk — відкриті "
        "дані й інструменти для української мови.",
    ),
    "contacts": (
        "Контакти",
        "Звʼяжіться зі спільнотою lang-uk: питання щодо продуктів, співпраця, "
        "пропозиції та підтримка.",
    ),
    "submit-product": (
        "Додати продукт до каталогу",
        "Створили корпус, модель чи бібліотеку для української мови? Поділіться "
        "своїм продуктом зі спільнотою lang-uk — заповніть коротку форму.",
    ),
    "usage-feedback": (
        "Розкажіть, як ви використовуєте наші продукти",
        "Використовуєте продукти lang-uk у дослідженнях чи бізнесі? Розкажіть "
        "нам — це допомагає розвивати відкриту українську NLP.",
    ),
}


def clip(text, limit=158):
    text = " ".join(str(text or "").split())
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(" ,;:.") + "…"


updated = []

for slug, (seo_title, descr) in META.items():
    page = Page.objects.filter(slug=slug).first()
    if page is None:
        print("!! missing page:", slug)
        continue
    changed = False
    if not page.seo_title or page.seo_title in STUBS:
        page.seo_title = seo_title
        changed = True
    if not page.search_description or page.search_description in STUBS:
        page.search_description = descr
        changed = True
    if changed:
        page.save()
        updated.append(page)

for artifact in ArtifactPage.objects.all():
    if artifact.search_description:
        continue
    descr = clip(artifact.short_description)
    if not descr:
        continue
    artifact.search_description = descr
    artifact.save()
    updated.append(artifact)

for page in updated:
    page = page.specific_class.objects.get(pk=page.pk)
    revision = page.save_revision()
    if page.live:
        revision.publish()

print("updated + republished:", len(updated))
