import threading
import logging
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.template import TemplateDoesNotExist

logger = logging.getLogger(__name__)


def _send_email(subject, to_email, context=None, html_template=None, html_string=None, from_email=None, attachments=None):
    """
    Core function to send an email with support for:
    - HTML templates
    - HTML strings
    - Attachments
    """
    from_email = from_email or settings.DEFAULT_FROM_EMAIL
    context = context or {}
    attachments = attachments or []

    # Determine content
    try:
        if html_template:
            html_content = render_to_string(html_template, context)
        elif html_string:
            html_content = html_string
        else:
            raise ValueError("Either 'html_template' or 'html_string' must be provided.")
    except TemplateDoesNotExist:
        logger.error(f"Template '{html_template}' does not exist.")
        return
    except Exception as e:
        logger.exception("Unexpected error when rendering email content.")
        return

    try:
        msg = EmailMultiAlternatives(subject, '', from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")

        # Attach files if provided
        for attachment in attachments:
            msg.attach(*attachment)  # (filename, content, mimetype)

        msg.send()
        logger.info(f"Email sent to {to_email} (subject: {subject})")
    except Exception as e:
        logger.exception(f"Failed to send email to {to_email}: {str(e)}")


def send_email_threaded(subject, to_email, context=None, html_template=None, html_string=None, from_email=None, attachments=None):
    """
    Sends an email in a separate thread.
    """
    thread = threading.Thread(
        target=_send_email,
        kwargs={
            'subject': subject,
            'to_email': to_email,
            'context': context,
            'html_template': html_template,
            'html_string': html_string,
            'from_email': from_email,
            'attachments': attachments
        }
    )
    thread.start()


def send_email_sync(subject, to_email, context=None, html_template=None, html_string=None, from_email=None, attachments=None):
    """
    Sends an email synchronously (blocking).
    """
    _send_email(
        subject=subject,
        to_email=to_email,
        context=context,
        html_template=html_template,
        html_string=html_string,
        from_email=from_email,
        attachments=attachments
    )

# send_email_threaded(
#     subject="Welcome!",
#     to_email="user@example.com",
#     context={"name": "John"},
#     html_template="emails/welcome.html"
# )

# send_email_sync(
#     subject="Thanks for joining",
#     to_email="user@example.com",
#     html_string=html_string
# )