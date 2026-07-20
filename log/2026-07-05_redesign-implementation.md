# Session log: 2026-07-05 — Redesign implementation (Phases A–I)

Executed the full plan from `log/plans/2026-07-05_new-design-completion.md`.
Everything verified on the local dev DB; nothing committed yet.

## What was built

**catalog app (new):**
- `ArtifactType` snippet (7 seeded via migration: corpora, dictionaries,
  gazetteers, services, libraries, models, datasets)
- `ArtifactPage` (type, short descriptions UA/EN, authors, license, stats,
  `last_significant_update` → "Нові надходження" badge, thumbnail, tags,
  typed `ArtifactLink` inline, search_fields)
- `SectionPage` (accordion listing, pagination 24/page, section badge)
- `ArtifactSubmission` + `UsageFeedback` moderation inboxes with Django admin,
  incl. "create draft page from submission" action
- `SubmitArtifactPage` + `FeedbackPage` public forms (reCAPTCHA, design-styled)
- `convert_product_pages` command (in-place ProductPage→SectionPage, --type-map)
- `import_artifacts` command (scrapes legacy live-site sections, adaptive
  h2/h3 split, EN matching, link extraction with kind guessing, static-URL
  absolutization). 23 artifacts imported locally.

**Design system integration:**
- `design_richtext` Jinja filter: wraps tables → `.table`, `<pre>` → `.copy`
  blocks with working copy-to-clipboard (JS already in bachoo_main.js)
- "code" rich-text feature enabled for editors
- `_includes/head.html`: `page_title` + `extra_css_files` context fallbacks
  for non-Wagtail views
- `bachoo_bare_base.html` for the distraction-free corpus reading view
- Homepage: new-arrivals badge wired; feedback + submit buttons wired
  (also in header CTA and become_a_part block via `submit_product_url()`)
- Header language switcher fixed for non-page views; search forms wired

**Migrated to new design:** corpus browser (4 templates, self-hosted Chartist,
vanilla JS chart init — no jQuery/CDN), search page (moved to Jinja2, URL
re-enabled, snippet results + pagination), 404 (bachoo + error_404.svg),
500 (self-contained, no DB deps).

**SendGrid:** django-anymail==10.3; production.py uses it when
SENDGRID_API_KEY env is set; recipients in GenericSiteSettings.notification_emails;
contact + submit + feedback forms all notify; failures logged, never break forms.

**Removed:** base.html, bare_base.html, lang-uk.css, custom.css, lang-uk-ie.css,
js/main.js, contents-list.js, static/images/converted, newborn app.
STATIC_ROOT (languk/static/) added to .gitignore.

## Gotchas discovered (worth remembering)
- uv upgraded Django to 5.x when installing anymail — pinned back to 4.1.8.
- treebeard `add_child` corrupts numchild if page validation fails mid-add —
  import wraps each artifact in a transaction now; `manage.py fixtree` repairs.
- modelcluster defers inline children until parent `.save()` — the admin
  action saves the page after creating links.
- Legacy live-site pages use `../../../../static/downloads/...` links — the
  importer absolutizes them to https://lang.org.ua/static/....
- `title_en` needed `blank=True` (TranslatedField already falls back EN→UA).

## Next steps
- Review UI visually in a browser (accordion animations, form styling).
- Commit (suggest slicing: catalog app / corpus+search / forms+mail / cleanup).
- Production rollout checklist → `migration.todo`.
