import json
import re
from datetime import datetime

from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.utils import formats, timezone
from django.urls import reverse, translate_url
from django.utils.translation import gettext, ngettext, override
from wagtailmenus.templatetags.menu_tags import main_menu, sub_menu


from dateutil.parser import parse as parse_dt
import markdown
from markupsafe import Markup
from jinja2 import Environment, pass_context
from jinja2.ext import Extension, nodes


class LanguageExtension(Extension):
    tags = {"language"}

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        # Parse the language code argument
        args = [parser.parse_expression()]
        # Parse everything between the start and end tag:
        body = parser.parse_statements(["name:endlanguage"], drop_needle=True)
        # Call the _switch_language method with the given language code and body
        return nodes.CallBlock(
            self.call_method("_switch_language", args), [], [], body
        ).set_lineno(lineno)

    def _switch_language(self, language_code, caller):
        with override(language_code):
            # Temporarily override the active language and render the body
            output = caller()
        return output


def ensure_aware(dt):
    if timezone.is_aware(dt):
        return dt
    else:
        return timezone.make_aware(dt)


def datetime_filter(dt, dayfirst=False):
    return (
        formats.date_format(
            timezone.localtime(
                ensure_aware(
                    parse_dt(dt, dayfirst=dayfirst) if isinstance(dt, str) else dt
                )
            ),
            "SHORT_DATETIME_FORMAT",
        )
        if dt
        else ""
    )


def date_filter(dt, dayfirst=False):
    return (
        formats.date_format(
            (
                timezone.localtime(ensure_aware(parse_dt(dt, dayfirst=dayfirst)))
                if isinstance(dt, str)
                else dt
            ),
            "SHORT_DATE_FORMAT",
        )
        if dt
        else ""
    )


def number_format(num):
    return "{:,.0f}".format(num)


def datetime_dumps(obj, *args, **kwargs):
    return json.dumps(obj, cls=DjangoJSONEncoder, *args, **kwargs)


def excerpt_markdown(text, lines=10):
    excerpt = text.split("\n")

    reminder = ""
    if len(excerpt) > lines:
        excerpt = excerpt[:lines]
        reminder = "\n..."

    return Markup("\n".join(excerpt).replace("#", "").strip() + reminder)


def markdown_filter(text):
    return Markup(markdown.markdown(text))


COPY_ICON_SVG = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="black" '
    'xmlns="http://www.w3.org/2000/svg">'
    '<rect x="9" y="9" width="12" height="12" rx="2"/>'
    '<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>'
    "</svg>"
)

TABLE_RE = re.compile(r"<table\b", re.IGNORECASE)
TABLE_CLOSE_RE = re.compile(r"</table>", re.IGNORECASE)
PRE_RE = re.compile(r"<pre\b[^>]*>(.*?)</pre>", re.IGNORECASE | re.DOTALL)


def design_richtext(html):
    """Post-process rendered rich text to match the Bachoo design system:
    wrap tables in .table scrollers and pre blocks in .copy blocks with a
    copy-to-clipboard button (wired up by bachoo_main.js)."""
    if not html:
        return html

    html = str(html)

    if '<div class="table">' not in html:
        html = TABLE_RE.sub('<div class="table"><table', html)
        html = TABLE_CLOSE_RE.sub("</table></div>", html)

    def wrap_pre(m):
        return (
            '<div class="copy code">'
            f'<pre class="copy__text code-text">{m.group(1)}</pre>'
            '<button class="copy__button" type="button" aria-label="Copy">'
            f'<span class="copy__icon">{COPY_ICON_SVG}</span>'
            f'<span class="copy__icon copy__icon--hover">{COPY_ICON_SVG}</span>'
            "</button></div>"
        )

    html = PRE_RE.sub(wrap_pre, html)

    return Markup(html)


def _form_page_urls(context):
    """URLs of the public form pages, resolved once per request (the header
    renders on every page, so this must not query per call)."""
    request = context.get("request")
    urls = getattr(request, "_form_page_urls", None)
    if urls is None:
        from catalog.models import FeedbackPage, SubmitArtifactPage

        submit = SubmitArtifactPage.objects.live().first()
        feedback = FeedbackPage.objects.live().first()
        urls = {
            "submit": submit.get_url(request) if submit else "#",
            "feedback": feedback.get_url(request) if feedback else "#",
        }
        if request is not None:
            request._form_page_urls = urls
    return urls


@pass_context
def submit_product_url(context):
    return _form_page_urls(context)["submit"]


@pass_context
def feedback_url(context):
    return _form_page_urls(context)["feedback"]


@pass_context
def switch_lang_url(context, lang_code):
    """Language-switcher target for non-Wagtail views (corpus, search):
    the same path re-prefixed for the target locale where possible."""
    request = context.get("request")
    if request is None:
        return f"/{lang_code}/"
    return translate_url(request.get_full_path(), lang_code)


def environment(**options):
    env = Environment(**options)
    env.globals.update(
        {
            "static": staticfiles_storage.url,
            "url": reverse,
            "submit_product_url": submit_product_url,
            "feedback_url": feedback_url,
            "switch_lang_url": switch_lang_url,
            "curr_year": datetime.today().year,
            "lang_uk_menu": pass_context(main_menu),
            "sub_menu": pass_context(sub_menu),
            "LANGUAGES_DICT": dict(settings.LANGUAGES),
        }
    )
    env.install_gettext_callables(gettext=gettext, ngettext=ngettext, newstyle=True)
    env.add_extension(LanguageExtension)

    env.policies["json.dumps_function"] = datetime_dumps

    env.filters.update(
        {
            "datetime": datetime_filter,
            "date": date_filter,
            "number_format": number_format,
            "excerpt_markdown": excerpt_markdown,
            "markdown": markdown_filter,
            "design_richtext": design_richtext,
        }
    )

    return env
