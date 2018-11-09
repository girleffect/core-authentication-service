import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from oidc_provider.signals import user_accept_consent

from authentication_service import api_helpers
from authentication_service.models import UserSite
from ge_event_log import events, schemas

logger = logging.getLogger(__name__)


@receiver(user_accept_consent)
def user_accepted_consent_callback(sender, user, client, **kwargs):
    site_id = api_helpers.get_site_for_client(client.id)
    # Make sure we have a UserSite entry, otherwise create one.
    _, created = UserSite.objects.get_or_create({}, user=user, site_id=site_id)
    message = "Created UserSite entry for {user} on {client}." if created \
        else "UserSite entry for {user} on {client} exists."
    logger.debug(message.format(user=user, client=client))


@receiver(user_logged_in)
def user_login_kinesis_callback(sender, request, user, **kwargs):
    events.put_event(
        event_type=schemas.EventTypes.USER_LOGIN,
        data={"user_id": str(user.id)},
        request=request
    )


@receiver(user_logged_out)
def user_logout_kinesis_callback(sender, request, user, **kwargs):
    events.put_event(
        event_type=schemas.EventTypes.USER_LOGOUT,
        data={"user_id": str(user.id)},
        request=request
    )
