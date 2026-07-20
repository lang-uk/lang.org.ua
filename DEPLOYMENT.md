# Deploying lang.org.ua

Deployed 2026-07-21 from the `new_version` branch: the Bachoo redesign, the
structured artifact catalog, public submit/feedback forms, Django 6.0 /
Wagtail 7.4 / Python 3.13, running in Docker behind the host nginx.

## Production layout (open-base)

| Piece | Where |
|---|---|
| Compose project | `/srv/sites/lang.org.ua/docker-compose.yml` (copy of `deploy/docker-compose.yml`) + `.env` + `local.py` |
| App container | `lang.org.ua:latest` image, host networking, gunicorn on `127.0.0.1:11234` (`APP_BIND`) behind the unchanged nginx vhost |
| PostgreSQL | `postgres:16-alpine` container on `127.0.0.1:5433`, data in `/srv/data/sites/lang.org.ua/pg16` (the host's system Postgres is 9.6 — below Django 6's floor — and keeps serving other tenants) |
| Redis | `redis:7-alpine` container on `127.0.0.2:6379` (the host's system Redis predates RESP3/HELLO; second loopback address keeps the standard port) |
| MongoDB | host `mongod`, reached via host networking (corpus browser) |
| Statics / media | `/srv/data/sites/lang.org.ua/{static,media}` mounted into the container; nginx serves them directly. The entrypoint refreshes statics on image version change |
| Build checkout | `/srv/sites/lang.org.ua-build` (git worktree of this repo) |
| Old deployment | `/srv/sites/lang.org.ua/{venv,languk}` + systemd `lang-org-ua-site.service` (disabled) + the 9.6 `lang-org-ua` DB — kept as rollback |

## Environment

`.env` (shared with the old deployment for rollback compatibility):
`DB_NAME/DB_USER/DB_PASS/DB_HOST`, `SECRET_KEY`, `SENTRY_DSN`,
`APP_WORKERS`, `DJANGO_SETTINGS_MODULE=languk.settings.production`,
`ALLOWED_HOSTS`, `BREVO_API_KEY` (form notifications; without it mail
stays on the console backend), old host-path `STATIC_ROOT`/`MEDIA_ROOT`
(overridden to `/static`/`/media` by compose).

Compose overrides per service: `DB_HOST=127.0.0.1`, `DB_PORT=5433`,
`REDIS_HOST=127.0.0.2`, `APP_BIND=127.0.0.1:11234`.

`local.py` (mounted to `/app/languk/settings/local.py`):
`RECAPTCHA_PUBLIC_KEY` / `RECAPTCHA_PRIVATE_KEY` — a **reCAPTCHA v3**
pair for lang.org.ua. Until set, the forms run on test-fallback keys
that accept everything.

## Deploying an update

```bash
cd /srv/sites/lang.org.ua-build
git fetch origin && git checkout origin/master -- .   # or the release branch
./build.sh                                            # tags lang.org.ua:latest

cd /srv/sites/lang.org.ua
cp /srv/sites/lang.org.ua-build/deploy/docker-compose.yml .   # if it changed
docker-compose up -d                                  # recreates on new image
docker exec $(docker-compose ps -q app) python manage.py migrate
```

## One-off admin commands

Compose v1 on this host cannot `docker-compose run` a host-networked
service (`host type networking can't be used with links`) — **use
`docker exec` on the running app container instead**:

```bash
docker exec -it $(docker-compose ps -q app) python manage.py <command>
```

## How the content got here

Production's database predated the redesign (nine static pages), so it
was **not** converted in place: the curated dev database — homepage
blocks, menus, 6+1 sections, 85 artifacts with authors/licenses/paper
links, form pages — was dumped (`deploy-payload/` on the dev machine),
restored into the pg16 container, and the dev-uploaded media unpacked
into the media dir. The wagtail Site record was then pointed at
`lang.org.ua:443`, and 27 permanent redirects map the old URLs
(`/{,uk/,en/}corpora` → `/uk/produkty/korpusi/` etc., about/team →
pro-nas, manifesto). The old prod DB survives untouched in the host 9.6.

The in-place conversion tooling (`convert_product_pages`,
`bootstrap_catalog_pages`, `import_artifacts`,
`import_community_artifacts --enrich`) remains in the repo for
DB-from-scratch scenarios; `pytest e2e/` covers the site end-to-end
(don't point the form tests at production — they POST real submissions).

## RQ workers (corpus jobs)

```bash
docker-compose --profile worker up -d    # rqworker languk_default, same image
```

## Rollback

Until the old stack is retired: `docker-compose stop app` +
`systemctl enable --now lang-org-ua-site` brings back the pre-redesign
site from the untouched venv and 9.6 database. MongoDB is shared and
unaffected. Backups: `/srv/backups/lang-org-ua.*.dump` (old prod),
`languk-dev.dump` (shipped content).
