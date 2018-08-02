import logging
import typing
import uuid
from datetime import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import signing
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils import timezone, translation
from django.utils.html import strip_tags
from django.utils.http import urlencode
from django.utils.translation import ugettext as _
from oidc_provider.models import Token, Code, UserConsent

from celery.task import task

from authentication_service.models import CoreUser, Organisation, UserSite

logger = logging.getLogger(__name__)

FROM_EMAIL = "auth@gehosting.org"

MAIL_TYPE_DATA = {
    "default": {
        "subject": _("Email from Girl Effect"),
        "from_email": FROM_EMAIL,
    },
    "password_reset": {
        "subject": _("Password reset for Girl Effect account"),
        "template_name": "registration/password_reset_email.html",
    },
    "delete_account": {
        "subject": "Account deletion",
        "template_name": "authentication_service/email/delete_account.html",
        # TODO GE mail address to be added.
        "recipients": ["ge@ge.com"]
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

    # The data used in the email are made up of default, type-specific and extra data.
    # Important: Make a copy of the default data to avoid manipulating the definitions.
    data = MAIL_TYPE_DATA["default"].copy()
    # Update the default data with type-specific data.
    data.update(MAIL_TYPE_DATA.get(mail_type, {}))
    # Update the data with what is specified in the "extra" data.
    data.update(extra)

    now = timezone.now().strftime("%a %d-%b-%Y|%H:%M:%S")
    recipients = data.get("recipients")
    subject = data.get("subject")
    from_email = data.get("from_email")
    cc = data.get("cc")
    template_name = data.get("template_name")

    # If there is not a recipient present, log the attempt and return nothing.
    # No use in attempting to mail without a recipient list.
    if not recipients:
        logger.error(f"Attempted to send an email of type '{mail_type}' without recipients")
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

    message = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=recipients,
        headers={"Unique-ID": uuid.uuid1().hex},
        cc=cc
    )

    # Alternate content is added if available.
    if extra.get("html_content", None) is not None:
        message.attach_alternative(extra.get("html_content", ""), "text/html")

    # Add attachments to the mail if needed.
    for attachment in extra.get("files", []):
        message.attach(*attachment)

    logger.info("Sent mail of type %s on %s" % (mail_type, now))
    message.send()


@task(name="invitation_email_task", default_retry_delay=300, max_retries=2)
def send_invitation_email(invitation: dict, registration_url: str, language=None) -> None:
    """
    Task to construct and send an invitation email.
    :param invitation: A dictionary representation of the Access Control Invitation model
    :param registration_url: An absolute URL to the registration page
    :param language: The code of the language in which the email must be sent, e.g. "en"
    """
    language = language or "en"
    with translation.override(language):
        sender = CoreUser.objects.get(pk=invitation["invitor_id"])
        recipient = invitation["email"]
        subject = _("Please create your Girl Effect account")

        # Create the registration URL
        # The payload is the data contained in the signed invitation
        payload = {
            "security": "high",
            "invitation_id": invitation["id"]
        }
        params = {
            "invitation": signing.dumps(payload, salt="invitation")
        }
        registration_url = registration_url + "?" + urlencode(params)

        context = invitation.copy()
        # Supplement the invitation context with extra information
        context["url"] = registration_url
        context["organisation"] = Organisation.objects.get(pk=invitation["organisation_id"])
        context["sender"] = sender

        # Generate the email from the template
        html_content = loader.render_to_string("authentication_service/email/invitation.html",
                                               context)
        text_content = strip_tags(html_content)
        message = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=FROM_EMAIL,
            reply_to=[sender.email],
            to=[recipient],  # Must be a list
            headers={"Unique-ID": uuid.uuid1().hex},
        )
        message.attach_alternative(html_content, "text/html")
        message.send()

        logger.info(f"Sent invitation from {sender.username} "
                    f"to {invitation['first_name']} {invitation['last_name']}")


@task(name="purge_expired_invitations_task")
def purge_expired_invitations(cutoff_date):
    """
    Task to call the purge_expired_invitations on the access_control API.
    :param cutoff_date: The cutoff_date for invitations.
    :return:
    """
    return settings.AC_OPERATIONAL_API.purge_expired_invitations(
        cutoff_date=cutoff_date
    )


@task(name="delete_user_and_data_task")
def delete_user_and_data_task(user_id: uuid.UUID, deleter_id: uuid.UUID, reason: str):
    """
    A task to clean up user-related data on the core components and remove
    the specified user profile itself.
    We keep track of deleted users (see the architecture documentation for the reasons)
    as the sites that they have visited.
    https://praekeltorg.atlassian.net/wiki/spaces/GECI/pages/477266059/Detailed+Architectural+Design#DetailedArchitecturalDesign-DeletionofUserData

    :param user_id: The user to delete.
    :param deleter_id: The user requesting the deletion.
    :param reason: The reason for the deletion.
    """
    user_data_store_api = settings.USER_DATA_STORE_API
    operational_api = settings.AC_OPERATIONAL_API

    # Cast UUIDs to strings, which can be used in both the API calls and
    # model lookups.
    user_id = str(user_id)
    deleter_id = str(deleter_id)

    try:
        user = CoreUser.objects.get(id=user_id)

        # Disable user
        user.is_active = False
        user.save()

        # Create DeletedUser entry
        user_data_store_api.deleteduser_create(
            data={
                "id": user_id,
                "deleter_id": deleter_id,
                "reason": reason
            })

        # Create DeletedSite entries
        for user_site in UserSite.objects.filter(user_id=user_id):
            user_data_store_api.deletedusersite_create(
                data={
                    "deleted_user_id": user_id,
                    "site_id": user_site.site.id,
                }
            )
        # Delete tokens
        Token.objects.filter(user_id=user_id).delete()

        # Delete consent
        UserConsent.objects.filter(user_id=user_id).delete()

        # Delete code
        Code.objects.filter(user_id=user_id).delete()

        # Delete UserSite entries
        UserSite.objects.filter(user_id=user_id).delete()

        # Delete User Data Store data
        result = user_data_store_api.delete_user_data(user_id)
        logger.debug(f"{result['amount']} rows deleted from User Data Store")

        # Delete Access Control data
        result = operational_api.delete_user_data(user_id)
        logger.debug(f"{result['amount']} rows deleted from Access Control")

        # Set the "deleted_at" value of the DeletedUser entity
        user_data_store_api.deleteduser_update(
            user_id, data={"deleted_at": datetime.utcnow()}
        )
    except CoreUser.DoesNotExist:
        logger.error(f"User {user_id} cannot be deleted because it does not exist.")