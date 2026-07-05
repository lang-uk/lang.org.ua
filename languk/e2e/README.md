# E2E tests (Playwright)

Browser-level tests for the redesigned lang.org.ua, covering the catalog
(section accordions, cards toggle, badges, artifact pages, copy-to-clipboard,
pagination), the public forms (submit-a-product, usage feedback, contact —
including the moderation inbox and editor notifications), search, language
switching, and the custom 404.

## Setup

```bash
uv pip install -r requirements-dev.txt
playwright install chromium
```

## Running

From `languk/`:

```bash
pytest                # spins up a live server + builds a test page tree
pytest --headed       # watch the browser
```

Requirements:

- local PostgreSQL (the suite creates/destroys a `test_languk` database);
- network access to google.com — the reCAPTCHA v3 widget mints its token
  client-side (the e2e settings use Google's universal test keys, so any
  token passes server verification).

## Corpus browser tests

The UberText browser reads from MongoDB, which the harness does not
provision. `test_corpus_live.py` therefore runs only against an already
populated server:

```bash
E2E_BASE_URL=http://127.0.0.1:8000 pytest e2e/test_corpus_live.py
```
