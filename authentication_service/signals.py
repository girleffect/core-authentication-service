import logging

from oidc_provider.signals import user_accept_consent

from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.conf import settings

from authentication_service import api_helpers
from authentication_service.constants import SessionKeys
from authentication_service.models import UserSite
from authentication_service.utils import get_session_data

from kinesis_conducer.producer_events import events, schemas

logger = logging.getLogger(__name__)


@receiver(user_accept_consent)
def user_accepted_consent_callback(sender, user, client, **kwargs):
    site_id = api_helpers.get_site_for_client(client.id)
    # Make sure we have a UserSite entry, otherwise create one.
    _, created = UserSite.objects.get_or_create({}, user=user, site_id=site_id)
    message = "Created UserSite entry for {user} on {client}." if created \
        else "UserSite entry for {user} on {client} exists."
    logger.debug(message.format(user=user, client=client))


def get_site_id(request):
    """
    Returns the site_id for the client found on the session.
    If no client was present on the request, assume the site is the
    Authentication Service itself.
    """
    client_id = get_session_data(request, SessionKeys.CLIENT_ID)
    site_id = settings.AUTHENTICATION_SERVICE_HARDCODED_SITE_ID
    if client_id:
        # NOTE: This will raise a ImproperlyConfigured if the site does not exist
        site_id = api_helpers.get_site_for_client(client_id)
    return site_id


@receiver(user_logged_in)
def user_login_kinesis_callback(sender, request, user, **kwargs):
    site_id = get_site_id(request)
    events.put_event(
        event_type=schemas.EventTypes.USER_LOGIN,
        site_id=site_id,
        user_id=str(user.id),
    )


@receiver(user_logged_out)
def user_logout_kinesis_callback(sender, request, user, **kwargs):
    site_id = get_site_id(request)
    events.put_event(
        event_type=schemas.EventTypes.USER_LOGOUT,
        site_id=site_id,
        user_id=str(user.id),
    )
