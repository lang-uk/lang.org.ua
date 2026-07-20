"""Curated public lang-uk projects from GitHub (github.com/lang-uk) and
Hugging Face (huggingface.co/lang-uk) to be published in the catalog.

Snapshot curated on 2026-07-05. Excluded: forks, site/infra repos, WIP
experiments, and projects already present in the catalog (ner-uk, tone-dict-uk,
tonal-model, ukrainian-word-stress-dictionary, vecs, vulyk, vulyk-ner, ...).

Details refreshed on 2026-07-20 from the GitHub API (contributors, licenses),
the Hugging Face API (model cards, commit history) and the ACL Anthology
(paper author lists): every entry now carries `authors` and, where published,
a link to the paper. Author names are given in Ukrainian for members of the
Ukrainian NLP community and as-published for foreign contributors.

Used by the 0005/0006 data migrations and the import_community_artifacts
command.
"""

GH = "https://github.com/lang-uk"
HF = "https://huggingface.co/lang-uk"
HFD = "https://huggingface.co/datasets/lang-uk"
HFS = "https://huggingface.co/spaces/lang-uk"
ACL = "https://aclanthology.org"

COMMUNITY_ARTIFACTS = [
    # ---------------------------------------------------------- libraries
    {
        "type": "libraries",
        "slug": "tokenize-uk",
        "title": "tokenize-uk — токенізація українських текстів",
        "title_en": "tokenize-uk — Ukrainian text tokenization",
        "description": "Проста та швидка Python-бібліотека для токенізації українських текстів: поділ на речення та слова.",
        "description_en": "Small and fast Python library to tokenize Ukrainian texts into sentences and words.",
        "license": "MIT",
        "authors": "Дмитро Чаплинський, Всеволод Дьомкін",
        "links": [("github", f"{GH}/tokenize-uk", "")],
    },
    {
        "type": "libraries",
        "slug": "ukrainian-word-stress",
        "title": "ukrainian-word-stress — розстановка наголосів",
        "title_en": "ukrainian-word-stress — word stress for Ukrainian",
        "description": "Python-бібліотека, що автоматично розставляє наголоси в українських текстах.",
        "description_en": "Python library that adds word stress marks to Ukrainian texts.",
        "license": "MIT",
        "authors": "Олексій Сивоконь, Дмитро Чаплинський",
        "links": [("github", f"{GH}/ukrainian-word-stress", "")],
    },
    {
        "type": "libraries",
        "slug": "ipa-uk",
        "title": "ipa-uk — фонетична транскрипція",
        "title_en": "ipa-uk — IPA transcription for Ukrainian",
        "description": "Python-пакет для генерації міжнародної фонетичної транскрипції (IPA) українських слів.",
        "description_en": "Python package to generate IPA (International Phonetic Alphabet) transcriptions for Ukrainian words.",
        "license": "MIT",
        "authors": "Дмитро Чаплинський, Данило Мисак",
        "links": [("github", f"{GH}/ipa-uk", "")],
    },
    {
        "type": "libraries",
        "slug": "choppa",
        "title": "choppa — SRX-сегментація речень",
        "title_en": "choppa — SRX sentence segmenter",
        "description": "Частковий Python-порт java SRX-сегментатора: правила поділу тексту на речення у форматі SRX.",
        "description_en": "Partial Python port of the Java SRX segmenter: rule-based sentence splitting in the SRX format.",
        "license": "MIT",
        "authors": "Дмитро Чаплинський, Володимир Кирилов",
        "links": [("github", f"{GH}/choppa", "")],
    },
    {
        "type": "libraries",
        "slug": "ukrainian-tts-preprocessing",
        "title": "Препроцесинг для українського TTS",
        "title_en": "Ukrainian TTS preprocessing",
        "description": "Інструменти та моделі для фонемізації українських текстів і передбачення лексичних наголосів — препроцесинг для синтезу мовлення.",
        "description_en": "Tools and models for Ukrainian phonemization and lexical stress prediction — preprocessing for text-to-speech.",
        "license": "Apache-2.0",
        "authors": "Анастасія Сеник, Михайло Лук'янчук, Валентина Робейко, Юрій Панів",
        "links": [
            ("github", f"{GH}/ukrainian-tts-preprocessing", ""),
            ("paper", f"{ACL}/2025.unlp-1.11/", "Стаття (UNLP 2025)"),
        ],
    },
    # ------------------------------------------------------------- models
    {
        "type": "models",
        "slug": "dragoman",
        "title": "Драгоман — англійсько-український переклад",
        "title_en": "Dragoman — English-Ukrainian translation model",
        "description": "SOTA-модель машинного перекладу з англійської на українську (PEFT/LoRA на базі Mistral), з онлайн-демо.",
        "description_en": "State-of-the-art English-to-Ukrainian machine translation model (PEFT/LoRA on top of Mistral), with an online demo.",
        "license": "Apache-2.0",
        "authors": "Юрій Панів, Дмитро Чаплинський, Нікіта Тринус, Володимир Кирилов",
        "links": [
            ("huggingface", f"{HF}/dragoman", "Модель"),
            ("demo", f"{HFS}/dragoman", "Демо"),
            ("huggingface", f"{HF}/dragoman-4bit", "4-bit версія"),
            ("github", f"{GH}/dragoman", "Код"),
            ("paper", f"{ACL}/2024.unlp-1.6/", "Стаття (UNLP 2024)"),
        ],
    },
    {
        "type": "models",
        "slug": "ukr-paraphrase-multilingual-mpnet-base",
        "title": "Семантичні вектори речень (sentence-transformers)",
        "title_en": "Ukrainian sentence embeddings (sentence-transformers)",
        "description": "Sentence-transformers модель для семантичних векторів українських речень на основі paraphrase-multilingual-mpnet.",
        "description_en": "Sentence-transformers model for semantic embeddings of Ukrainian sentences, based on paraphrase-multilingual-mpnet.",
        "license": "Apache-2.0",
        "authors": "Юрій Лаба, Володимир Мудрий, Дмитро Чаплинський, Мар'яна Романишин, Олесь Добосевич",
        "links": [
            ("huggingface", f"{HF}/ukr-paraphrase-multilingual-mpnet-base", ""),
            ("paper", f"{ACL}/2023.unlp-1.2/", "Стаття (UNLP 2023)"),
        ],
    },
    {
        "type": "models",
        "slug": "electra-base-ukrainian",
        "title": "ELECTRA-моделі для української мови",
        "title_en": "ELECTRA models for Ukrainian",
        "description": "Сімейство ELECTRA-base моделей, натренованих з нуля на українських текстах (дискримінатори та генератор).",
        "description_en": "A family of ELECTRA-base models pre-trained from scratch on Ukrainian texts (discriminators and a generator).",
        "license": "MIT",
        "authors": "Stefan Schweter",
        "links": [
            ("huggingface", f"{HF}/electra-base-ukrainian-cased-discriminator", "Дискримінатор"),
            ("huggingface", f"{HF}/electra-base-ukrainian-cased-generator", "Генератор"),
            ("huggingface", f"{HF}/electra-base-ukrainian-v2-cased-discriminator", "v2"),
            ("huggingface", f"{HF}/electra-base-ukrainian-v2-dbmdz-vocab-cased-discriminator", "v2 (dbmdz vocab)"),
        ],
    },
    {
        "type": "models",
        "slug": "omnigec-models",
        "title": "OmniGEC — виправлення граматичних помилок",
        "title_en": "OmniGEC — grammatical error correction models",
        "description": "Сімейство моделей OmniGEC для виправлення граматичних помилок (GEC) в українських текстах.",
        "description_en": "The OmniGEC family of grammatical error correction (GEC) models for Ukrainian.",
        "license": "MIT",
        "authors": "Роман Ковальчук, Мар'яна Романишин, Петро Іванюк",
        "links": [
            ("huggingface", f"{HF}/OmniGEC-Minimal-12B", "Minimal 12B"),
            ("huggingface", f"{HF}/OmniGEC-Minimal-8B", "Minimal 8B"),
            ("huggingface", f"{HF}/OmniGEC-Fluency-12B", "Fluency 12B"),
            ("huggingface", f"{HF}/OmniGEC-Fluency-8B", "Fluency 8B"),
            ("paper", f"{ACL}/2025.unlp-1.17/", "Стаття (UNLP 2025)"),
        ],
    },
    {
        "type": "models",
        "slug": "flair-uk-models",
        "title": "Flair-моделі для української",
        "title_en": "Flair models for Ukrainian",
        "description": "Моделі Flair для української мови: розпізнавання іменованих сутностей (NER), POS-тегінг та контекстні embeddings.",
        "description_en": "Flair models for Ukrainian: named entity recognition (NER), POS tagging and contextual string embeddings.",
        "license": "MIT",
        "authors": "Дмитро Чаплинський",
        "links": [
            ("huggingface", f"{HF}/flair-uk-ner", "NER"),
            ("huggingface", f"{HF}/flair-uk-pos", "POS"),
            ("huggingface", f"{HF}/flair-uk-forward", "Forward embeddings"),
            ("huggingface", f"{HF}/flair-uk-backward", "Backward embeddings"),
            ("huggingface", f"{HF}/flair-uk-forward-large", "Forward large"),
            ("huggingface", f"{HF}/flair-uk-backward-large", "Backward large"),
        ],
    },
    {
        "type": "models",
        "slug": "fasttext-uk",
        "title": "fastText-вектори для української",
        "title_en": "fastText vectors for Ukrainian",
        "description": "fastText-вектори слів для української мови, натреновані на корпусі UberText 2.0.",
        "description_en": "fastText word vectors for Ukrainian, trained on the UberText 2.0 corpus.",
        "license": "MIT",
        "authors": "Наталія Романишин, Дмитро Чаплинський, Кирило Захаров",
        "links": [
            ("huggingface", f"{HF}/fasttext_uk", "skip-gram"),
            ("huggingface", f"{HF}/fasttext_uk_cbow", "CBOW"),
            ("huggingface", f"{HF}/fasttext_uk_large", "large"),
            ("github", f"{GH}/fasttext-vectors-uk", "Код"),
            ("paper", f"{ACL}/2023.unlp-1.3/", "Стаття (UNLP 2023)"),
        ],
    },
    {
        "type": "models",
        "slug": "spacy-ner-ukrainian",
        "title": "SpaCy NER-моделі на трансформерах",
        "title_en": "Transformer-based spaCy NER models",
        "description": "SpaCy-моделі розпізнавання іменованих сутностей для української на основі RoBERTa-large, натреновані на корпусі NER-UK.",
        "description_en": "Transformer-based spaCy NER models for Ukrainian (RoBERTa-large), trained on the NER-UK corpus.",
        "license": "Apache-2.0 / MIT",
        "authors": "Владислав Радченко, Назарій Друщак, Наталія Романишин, Дмитро Чаплинський",
        "links": [
            ("huggingface", f"{HF}/roberta-large-ner-uk", "RoBERTa-large NER"),
            ("huggingface", f"{HF}/uk_ner_wechsel_minixhofer_roberta_large", "WECHSEL RoBERTa-large"),
        ],
    },
    {
        "type": "models",
        "slug": "ukr-clip",
        "title": "CLIP із підтримкою української",
        "title_en": "CLIP with Ukrainian support",
        "description": "CLIP-модель (ViT-H-14 + XLM-RoBERTa-large) з підтримкою української мови для zero-shot класифікації зображень.",
        "description_en": "CLIP model (ViT-H-14 + XLM-RoBERTa-large) supporting Ukrainian for zero-shot image classification.",
        "license": "MIT",
        "authors": "Юрій Лаба, Володимир Мудрий",
        "links": [("huggingface", f"{HF}/ukr-clip-vit-h-14-frozen-xlm-roberta-large-laion5B-s13B-b90k", "")],
    },
    # ------------------------------------------------------------ corpora
    {
        "type": "corpora",
        "slug": "malyuk",
        "title": "Малюк — корпус для тренування мовних моделей",
        "title_en": "Malyuk — Ukrainian LM pre-training corpus",
        "description": "Обʼєднаний корпус українських текстів (UberText 2.0, Oscar, Wikipedia та інші) для тренування великих мовних моделей.",
        "description_en": "Combined corpus of Ukrainian texts (UberText 2.0, Oscar, Wikipedia and more) for large language model pre-training.",
        "authors": "Дмитро Чаплинський",
        "links": [("huggingface", f"{HFD}/malyuk", "")],
    },
    {
        "type": "corpora",
        "slug": "court-decisions-uk",
        "title": "Корпус судових рішень",
        "title_en": "Ukrainian court decisions corpus",
        "description": "Корпус текстів судових рішень українською мовою.",
        "description_en": "A corpus of Ukrainian court decision texts.",
        "license": "MIT",
        "authors": "Андрій Руда",
        "links": [("huggingface", f"{HFD}/court-decisions-uk", "")],
    },
    {
        "type": "corpora",
        "slug": "1551-gov-ua",
        "title": "Корпус звернень до порталу 1551.gov.ua",
        "title_en": "1551.gov.ua municipal requests corpus",
        "description": "Датасет звернень громадян до порталу Київської міської ради 1551.gov.ua.",
        "description_en": "Dataset of citizen requests to the Kyiv City municipal portal 1551.gov.ua.",
        "authors": "Всеволод Дьомкін",
        "links": [("github", f"{GH}/1551.gov.ua", "")],
    },
    # ----------------------------------------------------------- datasets
    {
        "type": "datasets",
        "slug": "ubertext-ner-silver",
        "title": "UberText-NER-Silver — срібний NER-датасет",
        "title_en": "UberText-NER-Silver",
        "description": "Срібний NER-датасет, автоматично розмічений на текстах UberText 2.0.",
        "description_en": "Silver-standard NER dataset, automatically annotated over UberText 2.0 texts.",
        "license": "Apache-2.0",
        "authors": "Владислав Радченко, Назарій Друщак",
        "links": [("huggingface", f"{HFD}/UberText-NER-Silver", "")],
    },
    {
        "type": "datasets",
        "slug": "omnigec-corpora",
        "title": "Корпуси OmniGEC для виправлення помилок",
        "title_en": "OmniGEC corpora for grammatical error correction",
        "description": "Корпуси для тренування GEC-моделей: правки з Вікіпедії, Reddit та UberText.",
        "description_en": "Corpora for training GEC models: Wikipedia edits, Reddit and UberText data.",
        "license": "MIT",
        "authors": "Роман Ковальчук, Мар'яна Романишин, Петро Іванюк",
        "links": [
            ("huggingface", f"{HFD}/WikiEdits-MultiGEC", "WikiEdits-MultiGEC"),
            ("huggingface", f"{HFD}/Reddit-MultiGEC", "Reddit-MultiGEC"),
            ("huggingface", f"{HFD}/UberText-GEC", "UberText-GEC"),
            ("paper", f"{ACL}/2025.unlp-1.17/", "Стаття (UNLP 2025)"),
        ],
    },
    {
        "type": "datasets",
        "slug": "every-prompt",
        "title": "Every Prompt — датасет промптів",
        "title_en": "Every Prompt",
        "description": "Мільйон промптів, згенерованих зі структурованих даних вебу (How-to, FAQ, рецепти тощо).",
        "description_en": "A million prompts generated from structured web data (How-to, FAQ, recipes and more).",
        "license": "MIT",
        "authors": "Дмитро Чаплинський",
        "links": [("huggingface", f"{HFD}/every_prompt", "")],
    },
    {
        "type": "datasets",
        "slug": "recruitment-datasets-djinni",
        "title": "Датасети вакансій та кандидатів (Djinni)",
        "title_en": "Recruitment datasets (Djinni)",
        "description": "Анонімізовані профілі кандидатів та описи вакансій із сервісу Djinni, англійською та українською.",
        "description_en": "Anonymized candidate profiles and job descriptions from Djinni, in English and Ukrainian.",
        "license": "MIT",
        "authors": "Назарій Друщак, Мар'яна Романишин",
        "links": [
            ("huggingface", f"{HFD}/recruitment-dataset-candidate-profiles-english", "Кандидати (en)"),
            ("huggingface", f"{HFD}/recruitment-dataset-candidate-profiles-ukrainian", "Кандидати (uk)"),
            ("huggingface", f"{HFD}/recruitment-dataset-job-descriptions-english", "Вакансії (en)"),
            ("huggingface", f"{HFD}/recruitment-dataset-job-descriptions-ukrainian", "Вакансії (uk)"),
            ("paper", f"{ACL}/2024.unlp-1.2/", "Стаття (UNLP 2024)"),
        ],
    },
    {
        "type": "datasets",
        "slug": "mmzno",
        "title": "MMZNO — мультимодальний бенчмарк на базі ЗНО",
        "title_en": "MMZNO — multimodal benchmark from ZNO tests",
        "description": "Мультимодальний бенчмарк для оцінки моделей на завданнях зовнішнього незалежного оцінювання (ЗНО).",
        "description_en": "Multimodal benchmark for evaluating models on Ukrainian external independent testing (ZNO) tasks.",
        "license": "MIT",
        "authors": "Юрій Панів, Артур Кюлян, Дмитро Чаплинський, Микола Хандога, Антон Полішко, Тетяна Бас, Guillermo Gabrielli",
        "links": [
            ("huggingface", f"{HFD}/MMZNO", "Датасет"),
            ("github", f"{GH}/mmzno-benchmark", "Код"),
            ("paper", f"{ACL}/2025.unlp-1.2/", "Стаття (UNLP 2025)"),
        ],
    },
    {
        "type": "datasets",
        "slug": "paracrawl-3m",
        "title": "ParaCrawl 3M — паралельний корпус en-uk",
        "title_en": "ParaCrawl 3M English-Ukrainian parallel corpus",
        "description": "Три мільйони відфільтрованих паралельних англійсько-українських речень на основі ParaCrawl.",
        "description_en": "Three million filtered English-Ukrainian parallel sentence pairs based on ParaCrawl.",
        "authors": "Дмитро Чаплинський",
        "links": [("huggingface", f"{HFD}/paracrawl_3m", "")],
    },
    {
        "type": "datasets",
        "slug": "multi30k-extended-17k",
        "title": "Multi30k Extended — датасет перекладу",
        "title_en": "Multi30k Extended translation dataset",
        "description": "Розширена українська версія датасету Multi30k для мультимодального машинного перекладу.",
        "description_en": "Extended Ukrainian version of the Multi30k dataset for multimodal machine translation.",
        "license": "Apache-2.0",
        "authors": "Юрій Панів",
        "links": [("huggingface", f"{HFD}/multi30k-extended-17k", "")],
    },
    {
        "type": "datasets",
        "slug": "uacuisine",
        "title": "UACuisine — датасет українських рецептів",
        "title_en": "UACuisine — Ukrainian recipes dataset",
        "description": "Датасет українських кулінарних рецептів.",
        "description_en": "A dataset of Ukrainian culinary recipes.",
        "authors": "Юрій Панів, Артур Кюлян, Дмитро Чаплинський, Микола Хандога, Антон Полішко, Тетяна Бас, Guillermo Gabrielli",
        "links": [
            ("huggingface", f"{HFD}/UACuisine", ""),
            ("paper", f"{ACL}/2025.unlp-1.2/", "Стаття (UNLP 2025)"),
        ],
    },
    {
        "type": "datasets",
        "slug": "hypernymy-pairs",
        "title": "Пари гіперонімів української мови",
        "title_en": "Ukrainian hypernymy pairs",
        "description": "Датасет пар гіперонім-гіпонім для української мови.",
        "description_en": "A dataset of hypernym-hyponym pairs for Ukrainian.",
        "authors": "Наталія Романишин",
        "links": [("huggingface", f"{HFD}/hypernymy_pairs", "")],
    },
    # -------------------------------------------------------- dictionaries
    {
        "type": "dictionaries",
        "slug": "ukrainian-abbreviations-dictionary",
        "title": "Словник скорочень української мови",
        "title_en": "Dictionary of Ukrainian abbreviations",
        "description": "Словник скорочень (абревіатур) української мови.",
        "description_en": "Dictionary of abbreviations in the Ukrainian language.",
        "authors": "Олексій Сивоконь",
        "links": [("github", f"{GH}/ukrainian-abbreviations-dictionary", "")],
    },
    {
        "type": "dictionaries",
        "slug": "name-freq-dict-uk",
        "title": "Частотний словник імен та прізвищ",
        "title_en": "Frequency dictionary of Ukrainian names",
        "description": "Частотний словник українських імен та прізвищ.",
        "description_en": "Frequency dictionary of Ukrainian first and last names.",
        "license": "GPL-3.0",
        "authors": "Андрій Руда",
        "links": [("github", f"{GH}/name_freq_dict_uk", "")],
    },
    {
        "type": "dictionaries",
        "slug": "uk-gender-word-mapper",
        "title": "Відповідники фемінітивів та маскулінітивів",
        "title_en": "Ukrainian gender word mapper",
        "description": "Зіставлення гендерних пар слів (фемінітиви та маскулінітиви) української мови.",
        "description_en": "Mappings between gendered word pairs (feminitives and masculinitives) in Ukrainian.",
        "license": "MIT",
        "authors": "Ольга Нагурна",
        "links": [("github", f"{GH}/uk-gender-word-mapper", "")],
    },
    # ------------------------------------------------------------ services
    {
        "type": "services",
        "slug": "tokenize-ms",
        "title": "Мікросервіс токенізації",
        "title_en": "Tokenization microservice",
        "description": "Мікросервіс токенізації українських текстів на базі бібліотеки tokenize-uk.",
        "description_en": "Microservice for Ukrainian text tokenization based on the tokenize-uk library.",
        "license": "MIT",
        "authors": "Дмитро Чаплинський",
        "links": [("github", f"{GH}/tokenize-ms", "")],
    },
    {
        "type": "services",
        "slug": "ukrainian-llm-leaderboard",
        "title": "Лідерборд українських LLM",
        "title_en": "Ukrainian LLM leaderboard",
        "description": "Лідерборд великих мовних моделей на українських бенчмарках: метрики якості та порівняння моделей.",
        "description_en": "Leaderboard of large language models on Ukrainian benchmarks: quality metrics and model comparison.",
        "license": "MIT",
        "authors": "Юрій Панів",
        "links": [
            ("demo", f"{HFS}/ukrainian-llm-leaderboard", "Лідерборд"),
            ("github", f"{GH}/ukrainian-llm-leaderboard", "Код"),
            ("huggingface", f"{HFD}/ukrainian-llm-leaderboard-results", "Результати"),
            ("paper", f"{ACL}/2025.ranlp-1.100/", "Стаття (RANLP 2025)"),
        ],
    },
]


def populate(publish=False, log=None):
    """Create draft ArtifactPages for the curated community projects.
    Skips entries whose section does not exist yet or whose slug is taken.
    Returns (created, skipped) lists of slugs."""
    from catalog.models import SectionPage
    from catalog.utils import create_artifact_draft

    created, skipped = [], []
    for entry in COMMUNITY_ARTIFACTS:
        section = (
            SectionPage.objects.filter(artifact_type__slug=entry["type"])
            .order_by("pk")
            .first()
        )
        if section is None:
            skipped.append(entry["slug"])
            if log:
                log(f"no section for type '{entry['type']}' — skipped {entry['slug']}")
            continue

        artifact = create_artifact_draft(
            section,
            title=entry["title"],
            slug_source=entry["slug"],
            title_en=entry.get("title_en", ""),
            artifact_type=section.artifact_type,
            short_description=entry["description"],
            short_description_en=entry.get("description_en", ""),
            body=f"<p>{entry['description']}</p>",
            body_en=(
                f"<p>{entry['description_en']}</p>" if entry.get("description_en") else ""
            ),
            license=entry.get("license", ""),
            authors=entry.get("authors", ""),
            links=entry["links"],
            publish=publish,
        )
        if artifact is None:
            skipped.append(entry["slug"])
            if log:
                log(f"slug '{entry['slug']}' already exists — skipped")
        else:
            created.append(entry["slug"])
            if log:
                log(f"created {entry['slug']} in {section.slug}")
    return created, skipped


def enrich(log=None):
    """Backfill refreshed details onto artifact pages that already exist.

    Fills `authors` and `license` only where they are still blank (editor
    curation is never overwritten) and appends links whose URL the page does
    not have yet (e.g. the paper links). Draft pages get a fresh revision so
    the additions show up in the editor; live pages are republished.
    Returns the list of updated slugs."""
    from catalog.models import ArtifactLink, ArtifactPage

    updated = []
    for entry in COMMUNITY_ARTIFACTS:
        page = ArtifactPage.objects.filter(slug=entry["slug"]).first()
        if page is None:
            continue

        existing = list(page.links.all())
        links_changed = False
        # older imports created links with NULL sort_order, which Postgres
        # sorts after any explicit value — normalize by pk (insertion order)
        # so appended links actually land at the end
        if any(link.sort_order is None for link in existing):
            existing.sort(key=lambda link: link.pk)
            for order, link in enumerate(existing):
                if link.sort_order != order:
                    link.sort_order = order
                    link.save(update_fields=["sort_order"])
                    links_changed = True
        known = {link.url for link in existing}
        next_order = max((link.sort_order for link in existing), default=-1) + 1
        for kind, url, caption in entry["links"]:
            if url in known:
                continue
            ArtifactLink.objects.create(
                page=page, kind=kind, url=url, caption=caption, sort_order=next_order
            )
            next_order += 1
            links_changed = True

        # re-fetch so the revision serializes the fresh link set
        page = ArtifactPage.objects.get(pk=page.pk)
        changed = links_changed
        for field in ("authors", "license"):
            if entry.get(field) and not getattr(page, field):
                setattr(page, field, entry[field])
                changed = True
        if not changed:
            continue

        page.save()
        revision = page.save_revision()
        if page.live:
            revision.publish()
        updated.append(page.slug)
        if log:
            log(f"enriched {page.slug}")
    return updated
