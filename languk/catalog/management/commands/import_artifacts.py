import re

import requests
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand

from catalog.models import SectionPage
from catalog.utils import create_artifact_draft, guess_kind

# new-design section slug -> legacy live-site slug
SECTION_SOURCES = {
    "korpusi": "corpora",
    "slovniki": "dictionaries",
    "gazetiri": "gazetteers",
    "servisi": "services",
    "biblioteki": "libraries",
    "modeli": "models",
}

LICENSE_HEADINGS = ("ліцензія", "license", "licence")

RELATIVE_STATIC_RE = re.compile(r"(?:\.\./)+(static/)")


def absolutize_static(html, base_url):
    """Legacy pages point at hosted downloads with deep relative paths
    (../../../../static/downloads/...); rewrite them to absolute URLs so
    they work from any page depth and any environment."""
    return RELATIVE_STATIC_RE.sub(rf"{base_url}/\1", html)


def fetch_chunks(url, base_url):
    """Return [(title, chunk_html, chunk_soup), ...] parsed from a legacy
    section page. Sections with several h2 headings (corpora, dictionaries,
    models) keep one artifact per h2; sections whose h2 is just a group title
    (gazetteers, services, libraries) keep one artifact per h3."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    container = soup.select_one(".rte section") or soup.select_one(".rte")
    if container is None:
        return []

    split_tag = "h2" if len(container.find_all("h2")) >= 2 else "h3"

    chunks, current_title, current = [], None, []
    for el in container.children:
        name = getattr(el, "name", None)
        if name == split_tag:
            if current_title is not None:
                chunks.append((current_title, "".join(current)))
                current = []
            current_title = el.get_text(" ", strip=True)
        elif current_title is not None:
            current.append(str(el))
    if current_title is not None:
        chunks.append((current_title, "".join(current)))

    return [
        (title, html, BeautifulSoup(html, "html.parser"))
        for title, html in (
            (title, absolutize_static(html, base_url)) for title, html in chunks
        )
    ]


def extract_license(chunk_soup):
    for h3 in chunk_soup.find_all("h3"):
        if h3.get_text(strip=True).lower() in LICENSE_HEADINGS:
            sib = h3.find_next_sibling()
            if sib is not None:
                return sib.get_text(" ", strip=True)[:255]
    return ""


def extract_short_description(chunk_soup):
    p = chunk_soup.find("p")
    if p is None:
        return ""
    text = p.get_text(" ", strip=True)
    return text[:297] + "..." if len(text) > 300 else text


SIZE_CAPTION_RE = re.compile(r"^[\d.,]+\s*[kmgt]?b$", re.I)
ARCHIVE_EXT_RE = re.compile(r"\.(txt|csv|tsv|jsonl?)(\.(bz2|gz|xz|zip))?$", re.I)


def extract_links(chunk_soup):
    links, seen = [], set()
    for a in chunk_soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith(("#", "/", "mailto:")) or href in seen:
            continue
        seen.add(href)
        caption = a.get_text(" ", strip=True)[:255]
        # download tables use the file size as the anchor text — prefix the
        # archive name so the sidebar caption says what the file is
        if SIZE_CAPTION_RE.match(caption):
            stem = ARCHIVE_EXT_RE.sub("", href.rstrip("/").rsplit("/", 1)[-1])
            if stem:
                caption = f"{stem} ({caption})"[:255]
        links.append((guess_kind(href), href, caption))
    return links


EMPTY_CHUNK = ("", "", BeautifulSoup("", "html.parser"))


class Command(BaseCommand):
    help = (
        "Import artifacts from the legacy live-site section pages "
        "(lang.org.ua/uk/corpora/ etc.) into ArtifactPage entries under the "
        "matching SectionPage. Pages are created as drafts unless --publish. "
        "Idempotent: artifacts whose slug already exists are skipped."
    )

    def add_arguments(self, parser):
        parser.add_argument("--base-url", default="https://lang.org.ua")
        parser.add_argument(
            "--section",
            choices=sorted(SECTION_SOURCES),
            help="Import a single section (default: all)",
        )
        parser.add_argument("--publish", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        sections = (
            {options["section"]: SECTION_SOURCES[options["section"]]}
            if options["section"]
            else SECTION_SOURCES
        )
        total = 0
        for section_slug, legacy_slug in sections.items():
            try:
                section = SectionPage.objects.get(slug=section_slug)
            except SectionPage.DoesNotExist:
                self.stderr.write(f"SectionPage '{section_slug}' not found — skipping")
                continue

            base = options["base_url"].rstrip("/")
            try:
                uk_chunks = fetch_chunks(f"{base}/uk/{legacy_slug}/", base)
            except requests.RequestException as e:
                self.stderr.write(f"Failed to fetch {legacy_slug} (uk): {e}")
                continue
            try:
                en_chunks = fetch_chunks(f"{base}/en/{legacy_slug}/", base)
            except requests.RequestException:
                en_chunks = []
            # align EN chunks by position only when the page structure matches
            if len(en_chunks) != len(uk_chunks):
                en_chunks = [EMPTY_CHUNK] * len(uk_chunks)

            self.stdout.write(f"== {section_slug}: {len(uk_chunks)} artifacts on live site")

            for (title, chunk, soup), (title_en, chunk_en, soup_en) in zip(
                uk_chunks, en_chunks
            ):
                links = extract_links(soup)
                self.stdout.write(
                    f"  + {title!r} ({len(links)} links"
                    f"{', EN' if title_en else ''})"
                )
                if options["dry_run"]:
                    total += 1
                    continue

                artifact = create_artifact_draft(
                    section,
                    title=title,
                    slug_source=title_en or title,
                    title_en=title_en or "",
                    artifact_type=section.artifact_type,
                    body=chunk,
                    body_en=chunk_en,
                    short_description=extract_short_description(soup),
                    short_description_en=extract_short_description(soup_en),
                    license=extract_license(soup) or extract_license(soup_en),
                    links=links,
                    publish=options["publish"],
                )
                if artifact is None:
                    self.stdout.write(f"  '{title}' has no usable slug or exists — skipping")
                    continue
                total += 1

        suffix = " (dry run)" if options["dry_run"] else ""
        self.stdout.write(self.style.SUCCESS(f"Imported {total} artifacts{suffix}"))
