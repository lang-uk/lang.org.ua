import re

from django.db import transaction
from django.utils.text import slugify

LINK_KINDS = [
    (re.compile(r"github\.com", re.I), "github"),
    (re.compile(r"huggingface\.co", re.I), "huggingface"),
    (re.compile(r"arxiv\.org|aclanthology|doi\.org|academia\.edu", re.I), "paper"),
    (re.compile(r"\.(zip|gz|bz2|7z|xz|tar|csv|json|txt|bin|vec)([?#]|$)", re.I), "download"),
    (re.compile(r"lang\.org\.ua/(static|models|corpora)", re.I), "download"),
]


def guess_kind(url):
    for pattern, kind in LINK_KINDS:
        if pattern.search(url):
            return kind
    return "other"


def create_artifact_draft(section, title, links=(), publish=False, **fields):
    """Create an ArtifactPage under `section` with the given typed links.

    `links` is an iterable of (kind, url, caption) tuples or plain URL strings
    (kind is then guessed). Returns the page, or None when no usable slug can
    be made or a page with that slug already exists.
    """
    from catalog.models import ArtifactPage, SectionPage

    slug = slugify(fields.pop("slug_source", None) or title, allow_unicode=True)[:250]
    if not slug or ArtifactPage.objects.filter(slug=slug).exists():
        return None

    artifact = ArtifactPage(title=title, slug=slug, live=False, **fields)
    with transaction.atomic():
        # re-fetch: add_child mutates treebeard counters on the node
        parent = SectionPage.objects.get(pk=section.pk)
        parent.add_child(instance=artifact)
        for link in links:
            if isinstance(link, str):
                link = (guess_kind(link), link, "")
            kind, url, caption = link
            artifact.links.create(kind=kind, url=url, caption=caption)
        # modelcluster defers child rows until the parent is saved
        artifact.save()
        revision = artifact.save_revision()
        if publish:
            revision.publish()
    return artifact
