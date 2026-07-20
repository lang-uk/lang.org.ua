# One-shot content update, 2026-07-21: English translations for the four
# legacy artifacts that had none, plus EN captions for all Cyrillic link
# captions. Idempotent: only blank fields are filled.
#
# Run locally:   python manage.py shell < deploy/2026-07-21_translations.py
# Run on prod:   docker exec -i $(docker-compose ps -q app) \
#                    python manage.py shell < 2026-07-21_translations.py

from catalog.models import ArtifactPage

CAPTIONS_EN = {
    '"Словників України"': "Slovnyky Ukrainy",
    "Словників України": "Slovnyky Ukrainy",
    "4-bit версія": "4-bit version",
    "Андрій Рисін": "Andriy Rysin",
    "Артемом Крамовим": "Artem Kramov",
    "Браузер корпусу": "Corpus browser",
    "Вакансії (en)": "Job descriptions (en)",
    "Вакансії (uk)": "Job descriptions (uk)",
    "Володимир Гоцик": "Volodymyr Hotsyk",
    "Вулик": "Vulyk",
    "Генератор": "Generator",
    "Датасет": "Dataset",
    "Демо": "Demo",
    "Дискримінатор": "Discriminator",
    "Дмитро Гамбаль": "Dmytro Hambal",
    "Кандидати (en)": "Candidate profiles (en)",
    "Кандидати (uk)": "Candidate profiles (uk)",
    "Код": "Code",
    "Корпус розмічених даних": "Annotated corpus",
    "Лідерборд": "Leaderboard",
    "Михайло Чалий": "Mykhailo Chalyi",
    "Модель": "Model",
    "Мікросервіс NER": "NER microservice",
    "Мікросервіс WILD": "WILD microservice",
    "Мікросервіс на основі бібліотеки NLP_UK": "Microservice based on the NLP_UK library",
    "Олексій Сивоконь": "Oleksiy Syvokon",
    "Оцінка тональності слова": "Word sentiment scoring",
    "Пошук подібних слів": "Similar word search",
    "Результати": "Results",
    "Сергієм Шеховцовим": "Serhiy Shekhovtsov",
    "Словник": "Dictionary",
    "Стандартне розбиття на DEV і TEST набори": "Standard DEV/TEST split",
    "Стаття (RANLP 2025)": "Paper (RANLP 2025)",
    "Стаття (UNLP 2023)": "Paper (UNLP 2023)",
    "Стаття (UNLP 2024)": "Paper (UNLP 2024)",
    "Стаття (UNLP 2025)": "Paper (UNLP 2025)",
    "Сторінка корпусу та завантаження": "Corpus page and downloads",
    "Тетяни Кодлюк": "Tetiana Kodliuk",
    "анотований корпус": "annotated corpus",
    "бібліотеку MITIE": "MITIE library",
    "декларацій високопосадовців": "officials' asset declarations",
    "для російської мови": "for Russian",
    "для української мови": "for Ukrainian",
    "документацією по MITIE": "MITIE documentation",
    "нейромережева модель": "neural network model",
    "правилами": "rules",
    "прикладами використання": "usage examples",
    "розшифрувати": "transcribe",
    "словник": "dictionary",
    "тестові набори": "test sets",
    "тонального словнику": "tone dictionary",
    "тут": "here",
    "українського браунівського корпусу": "Ukrainian Brown corpus",
}

TRANSLATIONS = {
    "bert-моделі-від-сергія-тютюнника": {
        "title_en": "BERT models by Serhii Tiutiunnyk",
        "short_description_en": (
            "multi_cased_bert_base_uk.zip — a multilingual cased base BERT model "
            "fine-tuned on a combined Ukrainian dataset (SQuAD 2.0 and SDSJ 2017), "
            "achieving 61.2% exact answers on the squad-2.0-uk test set."
        ),
        "body_en": (
            '<p><a href="https://lang.org.ua/static/downloads/squad/multi_cased_bert_base_uk.zip">'
            "multi_cased_bert_base_uk.zip</a> — a multilingual cased base BERT model "
            "fine-tuned on a combined Ukrainian dataset (SQuAD 2.0 and SDSJ 2017) with "
            "the following parameters: epochs: 5, learning rate: 5e-5, max sequence "
            "length: 180, batch size: 16. Training used the script developed by the "
            "authors of the model (https://github.com/google-research/bert) and ran on "
            "an RTX 2080 Ti (11GB). On the squad-2.0-uk test set the model achieves "
            "61.2% exact answers.</p>"
        ),
    },
    "nerмоделі-для-mitie": {
        "title_en": "NER models for MITIE",
        "short_description_en": (
            "Thanks to our annotated corpus of Ukrainian we trained a model for "
            "automatic recognition of named entities (people, locations, "
            "organizations, etc.) in unseen texts, built on the open-source MITIE "
            "library."
        ),
        "body_en": (
            "<p>Thanks to our annotated corpus of Ukrainian we were able to train a "
            "model for automatic recognition of named entities (people, geographic "
            "names, company names, etc.) in unseen texts. For NER we chose the "
            '<a href="https://github.com/mit-nlp/MITIE/">MITIE library</a>. The library '
            "is open source, and its license permits free use even in commercial "
            "projects. MITIE also delivers high accuracy by combining familiar text "
            "features with CCA embeddings. Although MITIE is written in C++, it has "
            "bindings for other languages: C, Python, Java, Matlab. Please read the "
            '<a href="https://github.com/mit-nlp/MITIE/blob/master/README.md">MITIE '
            "documentation</a> and "
            '<a href="https://github.com/mit-nlp/MITIE/blob/master/examples/python/ner.py">'
            "usage examples</a> before you start.</p>"
            '<p>To compute the CCA embeddings we used <a href="/uk/corpora/">the corpus '
            "we collected</a> of Ukrainian news, Wikipedia articles and fiction.</p>"
            '<h3>Download the NER model <a href="https://lang.org.ua/static/downloads/ner_models/uk_model.dat.bz2">'
            "for Ukrainian</a></h3>"
            "<p> </p>"
            "<p>We also built a named entity recognition model for Russian, using the "
            '<a href="https://github.com/dialogue-evaluation/factRuEval-2016">annotated '
            "corpus</a> prepared by the organizers of the "
            '<a href="http://www.dialog-21.ru/evaluation/2016/ner/">Dialogue 2016</a> '
            "conference. For its CCA embeddings we used a corpus of Russian Wikipedia "
            "articles.</p>"
            '<h3>Download the NER model <a href="https://lang.org.ua/static/downloads/ner_models/ru_model.dat.bz2">'
            "for Russian</a></h3>"
            "<p> </p>"
        ),
    },
    "модель-розширення-тонального-словнику": {
        "title_en": "Tone dictionary expansion model",
        "short_description_en": (
            "A neural network model by Serhiy Shekhovtsov and Oles Petriv for "
            "expanding the tone dictionary: it finds words similar to existing ones "
            "using word2vec and lexvec vectors."
        ),
        "body_en": (
            '<p>To expand the <a href="https://github.com/lang-uk/tone-dict-uk">tone '
            'dictionary</a>, <a href="https://github.com/Serhiy-Shekhovtsov">Serhiy '
            "Shekhovtsov</a> and Oles Petriv built a "
            '<a href="https://github.com/lang-uk/tonal-model">neural network model</a> '
            "that finds words similar to existing ones using word2vec and lexvec "
            "vectors.</p>"
            "<p>Examples of working with the model and its data:</p>"
            "<ul>"
            '<li><a href="https://github.com/lang-uk/tonal-model/blob/master/examples/word2vec%20usage%20examples.ipynb">'
            "Similar word search</a></li>"
            '<li><a href="https://github.com/lang-uk/tonal-model/blob/master/examples/keras%20classifier%20usage%20examples.ipynb">'
            "Word sentiment scoring</a></li>"
            "</ul>"
        ),
    },
}

updated = []

for slug, fields in TRANSLATIONS.items():
    page = ArtifactPage.objects.filter(slug=slug).first()
    if page is None:
        print("!! missing page:", slug)
        continue
    changed = False
    for field, value in fields.items():
        if not str(getattr(page, field) or "").strip():
            setattr(page, field, value)
            changed = True
    if changed:
        page.save()  # persist now — the republish loop refetches
        updated.append(page)

# word-embeddings: title/body are already English-heavy; reuse them for EN,
# translating the Ukrainian fragments (and fixing one relative download URL)
we = ArtifactPage.objects.filter(slug="word-embeddings-word2vec-glove-lexvec").first()
if we is not None:
    body = str(we.body).replace(
        '../../../../downloads/models/fiction.cased.lemmatized.glove.300d.bz2',
        'https://lang.org.ua/static/downloads/models/fiction.cased.lemmatized.glove.300d.bz2',
    )
    if body != str(we.body):
        we.body = body
        we.save()
        if we not in updated:
            updated.append(we)
    if not str(we.body_en or "").strip():
        body_en = body
        for ua, en in [
            ("На базі зібраних нами корпусів новин, статей, художньої літератури, законів та юридичних текстів ми обчислили найпоширеніши word embeddings:",
             "From the corpora we collected — news, articles, fiction, laws and legal texts — we computed the most widely used word embeddings:"),
            ("(та його покращену версію", "(and its improved version"),
            (") й", ") and"),
            ("Ми вирішили опублікувати ці моделі, тому що їх обчислення займає доволі багато часу та серверних ресурсів.",
             "We publish these models because computing them takes considerable time and server resources."),
            ("Ми створили окремі моделі для кожної категорії текстів з 300d векторами. Ми також обчислили їх для лематизованих версій тих самих корпусів. Якщо вам потрібні інші налаштування моделей — скористайтеся корпусами, що ми підготували, та обчисліть моделі згідно ваших потреб.",
             "We built separate 300d models for every text category, and also computed them for lemmatized versions of the same corpora. If you need different model settings, take the corpora we prepared and compute the models to your needs."),
            ("<strong>Корпус</strong>", "<strong>Corpus</strong>"),
            ("<td>Художня література</td>", "<td>Fiction</td>"),
            ("<td>Новини</td>", "<td>News</td>"),
            ("<td>Уберкорпус</td>", "<td>Ubercorpus</td>"),
            ("За допомоги", "With the help of"),
            ("для оцінки якості побудованих векторів були створені",
             "we created"),
            ("аналогичні тим, які існували для англійської мови.",
             "for evaluating the quality of the vectors, analogous to those that existed for English."),
            ("Також були проведені оцінки якості, їх результати можна подивтись",
             "Quality evaluations were also performed; the results are available"),
            ("Параметри word2vec для малих корпусів (художня література):",
             "word2vec parameters for small corpora (fiction):"),
            ("Параметри lexvec для малих корпусів (художня література):",
             "lexvec parameters for small corpora (fiction):"),
            ("Параметри GloVe для малих корпусів (художня література):",
             "GloVe parameters for small corpora (fiction):"),
            ("Для великих корпусів minfreq дорівнює 25",
             "For large corpora, minfreq is 25"),
            ("Тетяни Кодлюк", "Tetiana Kodliuk"),
            ("тестові набори", "test sets"),
            ("тут", "here"),
        ]:
            body_en = body_en.replace(ua, en)
        we.body_en = body_en
        we.title_en = we.title_en or we.title
        we.short_description_en = we.short_description_en or (
            "From our corpora of news, fiction, laws and legal texts we computed "
            "the most widely used word embeddings — Word2Vec, its improved version "
            "LexVec, and GloVe — in 300d, for raw and lemmatized text."
        )
        we.save()  # persist now — the republish loop refetches
        if we not in updated:
            updated.append(we)

# captions: fill EN for every known Cyrillic caption across all artifacts
for page in ArtifactPage.objects.all():
    page_changed = False
    for link in page.links.all():
        cap = str(link.caption or "")
        if cap in CAPTIONS_EN and not link.caption_en:
            link.caption_en = CAPTIONS_EN[cap]
            link.save(update_fields=["caption_en"])
            page_changed = True
    if page_changed and page.slug not in [p.slug for p in updated]:
        updated.append(page)

for page in updated:
    page = ArtifactPage.objects.get(pk=page.pk)  # fresh links for the revision
    page.save()
    revision = page.save_revision()
    if page.live:
        revision.publish()

print("updated + republished:", len(updated))
print(sorted(p.slug for p in updated))
