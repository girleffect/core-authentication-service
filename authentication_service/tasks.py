from celery.task import task
import logging
import uuid

from django.contrib.contenttypes.models import ContentType
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils import timezone
from django.utils.translation import ugettext as _

logger = logging.getLogger()

MAILS = {
    "default": {
        "subject": _("Email from Girl Effect"),
        "from_email": "",
        "recipients": [""]
    },
    "password_reset": {
        "subject": _("Password reset for Girl Effect account"),
        "template_name": "registration/password_reset_email.html",
    },
    "delete_profile": {
        "subject": "",
        "template_name": "",
    },
}


# TODO add doc string
@task(name="email_task", default_retry_delay=300, max_retries=2)
def send_mail(context, mail_type, extra=None, objects_to_fetch=None):
    extra = extra or {}
    objects_to_fetch = objects_to_fetch or []
    default_data = MAILS["default"]
    type_data = MAILS.get(mail_type, {})
    now = timezone.now().strftime("%a %d-%b-%Y|%H:%M:%S")
    recipients = extra.get("recipients") or type_data.get(
        "recipients", default_data["subject"]
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

    if not recipients:
        logger.error(
            "Attempt to send an email without recipients; %s-%s" %
            (mail_type, now)
        )
        return
    if not isinstance(recipients, list):
        recipients = [recipients]

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
    message.attach_alternative(extra.get("html_content", ""), "text/html")
    for attachment in extra.get("files", []):
        message.attach(*attachment)

    logger.info("Sent mail of type %s on %s" % (mail_type, now))
    logger.info(message)
    message.send()
