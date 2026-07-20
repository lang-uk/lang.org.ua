# Deploying the redesigned lang.org.ua

This guide covers deploying the `new_version` branch: the Bachoo redesign,
the structured artifact catalog (`catalog` app), the public submit/feedback
forms, and the Django 6.0 / Wagtail 7.4 / Python 3.13 stack.

## What ships in this release

- Every public page on the new design; the old `base.html` design, its
  assets and the `newborn` app are deleted.
- Products live in a data model (`ArtifactType` / `SectionPage` /
  `ArtifactPage`) instead of rich-text pages; community submissions and
  usage feedback flow into moderation inboxes in the Django admin with
  SendGrid notifications.
- Django 6.0.6, Wagtail 7.4.2, Python 3.13; `raven` replaced by
  `sentry-sdk`, `django-redis-cache` by Django's built-in Redis backend.

## Prerequisites

- PostgreSQL (the relational DB), Redis (cache + RQ queues), MongoDB
  (the UberText corpus browser).
- Docker for the image build; the image bundles gunicorn, the compiled
  corpus-pipeline deps (`gcld3`, `ufal.udpipe`) and pre-collected statics.

## 1. Build the image

```bash
./build.sh          # tags with git describe, passes VERSION=git sha
```

The image serves HTTP on port 8000, exposes `/static` and `/media` volumes,
and `docker-entrypoint.sh` copies collected statics into the `/static`
volume on version change. `APP_WORKERS` (default 2) controls gunicorn.

## 2. Environment

| Variable | Purpose |
|---|---|
| `DB_NAME` / `DB_USER` / `DB_PASS` / `DB_HOST` / `DB_PORT` | PostgreSQL |
| `MONGODB_HOST` (host:port), `MONGODB_DB`, `MONGODB_USERNAME`, `MONGODB_PASSWORD`, `MONGODB_AUTH_DB` | UberText MongoDB |
| `REDIS_HOST` | cache + RQ queues (db 0, port 6379) |
| `SECRET_KEY` | **set it** — base.py has an insecure default |
| `ALLOWED_HOSTS` | space-separated (see note below) |
| `SENTRY_DSN`, `VERSION` | error reporting (sentry-sdk, production settings only) |
| `SENDGRID_API_KEY` | form notifications; without it mail stays on the console backend |
| `DEFAULT_FROM_EMAIL` | sender for notifications (default no-reply@lang.org.ua) |
| `STATIC_ROOT` / `MEDIA_ROOT` | preset in the image (`/static`, `/media`) |
| `DJANGO_SETTINGS_MODULE` | `languk.settings.production` (wsgi.py default) |

reCAPTCHA keys are not env-driven: provide
`languk/languk/settings/local.py` with `RECAPTCHA_PUBLIC_KEY` /
`RECAPTCHA_PRIVATE_KEY` (production.py imports it), as before.

> Note: base.py currently hard-overrides `ALLOWED_HOSTS = ["*"]` right
> after reading the env var — a pre-existing wart. If you want real host
> validation, delete that line.

## 3. First deploy of this release (one-time data steps, in order)

**Back up PostgreSQL first** — this release applies Wagtail 5.2→7.4
migrations plus the catalog migrations, and step 2 rewrites the page tree
in place; there is no practical way back but a restore.

```bash
manage.py migrate

# 1. legacy ProductPage sections -> SectionPage (preserves ids/slugs/URLs)
manage.py convert_product_pages --type-map \
    korpusi=corpora slovniki=dictionaries gazetiri=gazetteers \
    servisi=services biblioteki=libraries modeli=models

# 2. Датасети section + submit-a-product + usage-feedback pages
manage.py bootstrap_catalog_pages

# 3. artifacts scraped from the legacy site pages (created as drafts)
manage.py import_artifacts

# 4. 30 curated GitHub/Hugging Face projects, complete with authors,
#    licenses and paper links (drafts; the 0005/0007 migrations already
#    tried this but skipped types whose sections didn't exist yet;
#    --enrich backfills blank authors/licenses/links on existing pages)
manage.py import_community_artifacts
```

Then in the CMS/admin:

1. Wagtail admin → Settings → Generic site settings → fill
   **notification_emails** (comma-separated editor addresses).
2. Curate the imported drafts (Сторінки → Продукти → sections): EN texts
   for the models section, `last_significant_update` dates (drives the
   "Нові надходження" badge), licenses/authors on the legacy-scraped
   artifacts (the 30 community ones already carry authors, licenses and
   paper links), trim duplicate download links on link-heavy artifacts —
   then publish.
3. Clear the legacy one-word section bodies (they repeat the title) and
   give the Датасети section an SVG icon for its homepage card.
4. Old rich-text section content stays reachable until you publish the new
   artifact pages; slugs never changed, so no redirects are needed.

## 4. Verify

Spot-check: `/uk/`, `/uk/produkty/` + each section, one artifact page,
`/uk/submit-product/` and `/uk/usage-feedback/` (submit a test entry —
check the admin inbox and the notification email), `/uk/search/?query=...`,
`/corpus/` down to an article reading view, `/en/` variants, a 404.

The read-only corpus e2e tests can run against production:

```bash
cd languk && E2E_BASE_URL=https://lang.org.ua pytest e2e/test_corpus_live.py
```

Do **not** point the rest of the e2e suite at production — the form tests
POST real submissions. The full suite runs locally against its own
database: `cd languk && pytest` (see `e2e/README.md`).

## 5. RQ workers

Corpus background jobs (export, UDPipe tagging, NLP-UK, frequency vocab)
need an RQ worker from the same image (`gcld3`/`ufal.udpipe` are compiled
into it):

```bash
docker run ... languk:TAG python manage.py rqworker languk_default
```

## Rollback

Redeploy the previous image **and restore the PostgreSQL backup** — the
Wagtail 7 migrations and the page-tree conversion are not reversible in
practice. MongoDB and Redis are untouched by this release.
