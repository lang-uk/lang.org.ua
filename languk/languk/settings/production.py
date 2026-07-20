from __future__ import absolute_import, unicode_literals

import os

from .base import *

DEBUG = False

# Error reporting (replaces the long-dead raven client)
if os.environ.get("SENTRY_DSN"):
    import sentry_sdk

    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"],
        release=os.environ.get("VERSION", "undef"),
    )

# Form notifications (contact, artifact submissions, usage feedback) go out
# through Brevo; without BREVO_API_KEY mail silently stays on the
# console backend from base.py
if os.environ.get("BREVO_API_KEY"):
    EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
    ANYMAIL = {
        "BREVO_API_KEY": os.environ["BREVO_API_KEY"],
    }

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "no-reply@lang.org.ua")

try:
    from .local import *
except ImportError:
    pass
