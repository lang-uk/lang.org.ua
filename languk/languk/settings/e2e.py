"""Settings for the Playwright e2e suite (languk/e2e/).

Based on dev, but: DEBUG off (so the custom 404 renders and no debug
toolbar), Google's universal reCAPTCHA test keys (the widget still needs
network access to google.com to mint a token), and in-memory email.
"""
from __future__ import absolute_import, unicode_literals

from .dev import *

DEBUG = False

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]

# dev.py added these under DEBUG = True
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]
MIDDLEWARE = [m for m in MIDDLEWARE if "debug_toolbar" not in m]

# Google's documented always-pass test keys
RECAPTCHA_PUBLIC_KEY = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
RECAPTCHA_PRIVATE_KEY = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"
SILENCED_SYSTEM_CHECKS = ["django_recaptcha.recaptcha_test_key_error"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
