from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils import formats, timezone
from django.urls import reverse
from django.conf import settings
from django.utils.translation import gettext, ngettext, override

from dateutil.parser import parse as parse_dt
from jinja2 import Environment
from jinja2.ext import Extension, nodes


class LanguageExtension(Extension):
    tags = {'language'}

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        # Parse the language code argument
        args = [parser.parse_expression()]
        # Parse everything between the start and end tag:
        body = parser.parse_statements(['name:endlanguage'], drop_needle=True)
        # Call the _switch_language method with the given language code and body
        return nodes.CallBlock(self.call_method('_switch_language', args), [], [], body).set_lineno(lineno)

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
            timezone.localtime(ensure_aware(parse_dt(dt, dayfirst=dayfirst) if isinstance(dt, str) else dt)),
            "SHORT_DATETIME_FORMAT",
        )
        if dt
        else ""
    )


def date_filter(dt, dayfirst=False):
    return (
        formats.date_format(
            timezone.localtime(ensure_aware(parse_dt(dt, dayfirst=dayfirst) if isinstance(dt, str) else dt)),
            "SHORT_DATE_FORMAT",
        )
        if dt
        else ""
    )

def environment(**options):
    env = Environment(**options)
    env.globals.update({
        "static": staticfiles_storage.url,
        "url": reverse,
    })
    env.install_gettext_callables(gettext=gettext, ngettext=ngettext, newstyle=True)
    env.add_extension(LanguageExtension)

    env.filters.update(
        {
            "datetime": datetime_filter,
            "date": date_filter,
        }
    )

    return env
