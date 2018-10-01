import logging
import typing
import uuid
from datetime import datetime

from celery.task import task
from django.utils.dateparse import parse_datetime
from oidc_provider.models import Token, Code, UserConsent

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core import signing
from django.core.mail import EmailMultiAlternatives
from django.forms import model_to_dict
from django.template import loader
from django.utils import timezone, translation
from django.utils.html import strip_tags
from django.utils.http import urlencode
from django.utils.translation import ugettext as _

from authentication_service.models import Organisation, UserSite, UserSecurityQuestion
from access_control.rest import ApiException as AccessControlApiException
from user_data_store.rest import ApiException as UserDataStoreApiException

logger = logging.getLogger(__name__)

FROM_EMAIL = "auth@gehosting.org"

UserModel = get_user_model()

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
    "request_client_creation": {
        "subject": "Client creation request",
        "template_name": "request_client/email/request_client.html",
        "recipients": settings.CLIENT_REQUEST_EMAIL
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
        sender = UserModel.objects.get(pk=invitation["invitor_id"])
        recipient = invitation["email"]
        subject = _("Please create your Girl Effect account")

        # Create the registration URL
        # The payload is the data contained in the signed invitation
        payload = {
            "security": "high",
            "invitation_id": invitation["id"]
        }
        if "redirect_url" in invitation:
            payload["redirect_url"] = invitation["redirect_url"]

        params = {
            "invitation": signing.dumps(payload, salt="invitation"),
        }

        registration_url = registration_url + "?" + urlencode(params)

        context = invitation.copy()
        # Supplement the invitation context with extra information
        context["url"] = registration_url
        context["organisation"] = Organisation.objects.get(pk=invitation["organisation_id"])
        context["sender"] = sender
        if isinstance(context["expires_at"], str):
            # Convert expires_at from string to datetime. This way we can tweak the template in terms
            # of rendering.
            context["expires_at"] = parse_datetime(context["expires_at"])

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


@task(name="purge_expired_invitations_task",
      default_retry_delay=5 * 60,
      autoretry_for=(AccessControlApiException,),
      retry_backoff=True,
      retry_backoff_max=600,
      retry_jitter=True)
def purge_expired_invitations(cutoff_date):
    """
    Task to call the purge_expired_invitations on the access_control API.
    :param cutoff_date: The cutoff_date for invitations.
    :return:
    """
    result = settings.AC_OPERATIONAL_API.purge_expired_invitations(
        cutoff_date=cutoff_date
    )
    logger.info(f"Purged {result.amount} invitations.")


@task(name="delete_user_and_data",
      default_retry_delay=5 * 60,
      autoretry_for=(AccessControlApiException, UserDataStoreApiException),
      retry_backoff=True,
      retry_backoff_max=600,
      retry_jitter=True)
def delete_user_and_data_task(user_id: uuid.UUID, deleter_id: uuid.UUID, reason: str):
    """
    A task to clean up user-related data on the core components and remove
    the specified user profile itself.
    We keep track of deleted users (see the architecture documentation for the reasons)
    as the sites that they have visited.
    https://praekeltorg.atlassian.net/wiki/spaces/GECI/pages/477266059/Detailed+Architectural+Design#DetailedArchitecturalDesign-DeletionofUserData

    IMPORTANT: This function is written so that it is idempotent, i.e. it can be run repeatedly
    without any unwanted side-effects. The reason is that, should something fail (like an API call),
    this task can be retried at a later stage.

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
        user = UserModel.objects.get(id=user_id)

        # Disable user
        user.is_active = False
        user.save()
    except UserModel.DoesNotExist:
        logger.error(f"User {user_id} cannot be deleted because it does not exist.")
        return  # Nothing to do

    # Check if this job has been attempted before.
    try:
        deleted_user = user_data_store_api.deleteduser_read(user_id)
    except UserDataStoreApiException as e:
        if e.status == 404:
            deleted_user = None
        else:
            raise

    if deleted_user is None:
        # Create DeletedUser entry
        data = {
            "id": user_id,
            "username": user.username,
            "deleter_id": deleter_id,
            "reason": reason
        }
        if user.email:
            data["email"] = user.email

        if user.msisdn:
            data["msisdn"] = user.msisdn

        user_data_store_api.deleteduser_create(data=data)

    # Create DeletedSite entries
    for user_site in UserSite.objects.filter(user_id=user_id):
        try:
            deleted_user_site = user_data_store_api.deletedusersite_read(user_id, user_site.site_id)
        except UserDataStoreApiException as e:
            if e.status == 404:
                deleted_user_site = None
            else:
                raise

        if deleted_user_site is None:
            user_data_store_api.deletedusersite_create(
                data={
                    "deleted_user_id": user_id,
                    "site_id": user_site.site_id,
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

    # Delete UserSecurityQuestion entries
    UserSecurityQuestion.objects.filter(user_id=user_id).delete()

    # Delete Access Control data
    result = operational_api.delete_user_data(user_id)
    logger.debug(f"{result.amount} rows deleted from Access Control")

    # Delete User Data Store data and set the "deleted_at" value
    # of the DeletedUser entity.
    result = user_data_store_api.delete_user_data(user_id)
    logger.debug(f"{result.amount} rows deleted from User Data Store")

    user_data_store_api.deleteduser_update(
        user_id, data={"deleted_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}
    )

    # Keep a copy of some of the fields for the email notification
    user_dict = model_to_dict(user, fields=[
        "id", "username", "first_name", "last_name"
    ])
    # For some reason model_to_dict does not include the id. Add it explicitly.
    user_dict["id"] = user_id

    # Finally, delete the user
    user.delete()

    # We try to send a confirmation email to the user requesting the deletion.
    # If it fails, we cannot retry
    try:
        deleter = UserModel.objects.get(id=deleter_id)
        deleter_dict = model_to_dict(deleter, fields=[
            "username", "first_name", "last_name", "email"
        ])
        if deleter.email:
            send_deletion_confirmation_task.delay(
                user_dict, deleter_dict
            )
            logger.info(f"Queued deletion confirmation for {user_dict['username']} ({user_dict['id']})"
                        f" to {deleter.first_name} {deleter.last_name} ({deleter.email})")
    except UserModel.DoesNotExist:
        logger.error(f"User {deleter_id} cannot be found, so we cannot send an email.")


@task(name="send_deletion_confirmation",
      default_retry_delay=5 * 60,
      retry_backoff=True,
      retry_backoff_max=600,
      retry_jitter=True)
def send_deletion_confirmation_task(
    user: dict,
    deleter: dict,
):
    subject = _("Confirmation of user and data deletion")

    # Generate the email from the template
    html_content = loader.render_to_string(
        "authentication_service/email/deletion_confirmation.html",
        {"user": user, "deleter": deleter}
    )
    text_content = strip_tags(html_content)
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=FROM_EMAIL,
        reply_to=["no-reply@gehosting.org"],
        to=[deleter["email"]],  # Must be a list
        headers={"Unique-ID": uuid.uuid1().hex},
    )
    message.attach_alternative(html_content, "text/html")
    message.send()

    logger.info(f"Sent deletion confirmation for {user['username']} ({user['id']})"
                f" to {deleter['first_name']} {deleter['last_name']} ({deleter['email']})")
