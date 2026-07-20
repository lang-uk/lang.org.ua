import logging

from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def notify_editors(subject, body, request=None):
    """Send a notification to the editor addresses configured in
    GenericSiteSettings.notification_emails. Never raises: a mail failure
    must not break form submission."""
    from home.models import GenericSiteSettings

    try:
        config = GenericSiteSettings.load(request_or_site=request)
        recipients = [
            email.strip()
            for email in (config.notification_emails or "").split(",")
            if email.strip()
        ]
        if not recipients:
            logger.info("No notification_emails configured; skipping '%s'", subject)
            return
        # from_email=None -> settings.DEFAULT_FROM_EMAIL
        send_mail(subject, body, None, recipients)
    except Exception:
        logger.exception("Failed to send editor notification '%s'", subject)
