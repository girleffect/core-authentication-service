import logging
import typing
import uuid

from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils import timezone
from django.utils.translation import ugettext as _

from celery.task import task

logger = logging.getLogger()

MAIL_TYPE_DATA = {
    "default": {
        "subject": _("Email from Girl Effect"),
        "from_email": "",
        # TODO GE mail address to be added.
        "recipients": ["ge@ge.com"]
    },
    "password_reset": {
        "subject": _("Password reset for Girl Effect account"),
        "template_name": "registration/password_reset_email.html",
    },
    "delete_account": {
        "subject": "Account deletion",
        "template_name": "authentication_service/email/delete_account.html",
    },
}


@task(name="email_task", default_retry_delay=300, max_retries=2)
def send_mail(
        context: dict,
        mail_type: str,
        extra: dict = None,
        objects_to_fetch: typing.List[dict] = None):
    """
    Task to construct and send emails.

    context: context to be passed to the email template.
    mail_type: key for a managed dict containing default settings for certain mail types.
    extra: Overrides the default mail type setting if needed.
    objects_to_fetch: Django model instances do not serialise well. This is a
        list containing dicts to allow instances to be fetched from within this
        task.
        [
            {
                "app_label": instance._meta.app_label,
                "model": instance._meta.model_name,
                "id": instance.id,
                "context_key": "key",
            }
        ]
    """
    # Assign instance variables.
    extra = extra or {}
    objects_to_fetch = objects_to_fetch or []
    default_data = MAIL_TYPE_DATA["default"]
    type_data = MAIL_TYPE_DATA.get(mail_type, {})
    now = timezone.now().strftime("%a %d-%b-%Y|%H:%M:%S")
    recipients = extra.get("recipients") or type_data.get(
        "recipients", default_data["recipients"]
    )
    subject = extra.get("subject") or type_data.get(
        "subject", default_data["subject"]
    )
    from_mail = extra.get("from_mail") or type_data.get(
        "from_email", default_data["from_email"]
    )
    template_name = extra.get("template_name") or type_data.get(
        "template_name"
    )

    # If there is not a recipient present, log the attempt and return nothing.
    # No use in attempting to mail without a recipient list.
    if not recipients:
        logger.error(
            "Attempt to send an email without recipients; %s-%s" %
            (mail_type, now)
        )
        return

    # Fetches instance for each object from the db and puts it into
    # context, that gets passed to the email template.
    for obj in objects_to_fetch:
        obj_type = ContentType.objects.get(
            app_label=obj["app_label"],
            model=obj["model"]
        )
        model_class = obj_type.model_class()
        instance = model_class.objects.get(id=obj["id"])
        context[obj.get("context_key", obj["model"].lower())] = instance
    text_content = loader.render_to_string(template_name, context)
    cc = extra.get("cc") or type_data.get("cc")

    message = EmailMultiAlternatives(
        subject,
        text_content,
        from_mail,
        recipients,
        headers={"Unique-ID": uuid.uuid1()},
        cc=cc
    )

    # Alternate content is added if available.
    message.attach_alternative(extra.get("html_content", ""), "text/html")

    # Add attachments to the mail if needed.
    for attachment in extra.get("files", []):
        message.attach(*attachment)

    logger.info("Sent mail of type %s on %s" % (mail_type, now))
    message.send()
