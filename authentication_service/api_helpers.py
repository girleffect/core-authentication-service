import types
import logging

from django.conf import settings
from django.core import exceptions

from access_control.rest import ApiException as AccessControlApiException
from user_data_store.rest import ApiException as UserDataStoreApiException


LOGGER = logging.getLogger(__name__)


def create_user_site_data(user_id, site_id):
    return settings.USER_DATA_STORE_API.usersitedata_create(data={
        "user_id": user_id, "site_id": site_id, "data": {}
    })


def is_site_active(client):
    """Check if the site associated with the specified client id is enabled.
    :param client: OIDC Client
    :return: boolean
    """
    try:
        sites = settings.ACCESS_CONTROL_API.site_list(client_id=client.id)
    except AccessControlApiException as e:
        LOGGER.error(str(e))
        return False

    if sites:
        return sites[0].is_active

    raise exceptions.ImproperlyConfigured(
        f"Site for client.id ({client.id}) not found"
    )


def get_site_for_client(client_id):
    """
    Return the id of the Site linked to the Client identified by client_id.
    :param client_id: The Client ID
    :return:  The Site ID
    """
    try:
        sites = settings.ACCESS_CONTROL_API.site_list(client_id=client_id)
        if len(sites) == 1:  # It is not necessary to check if the site is active.
            return sites[0].id

        raise exceptions.ImproperlyConfigured(
            f"Site for client.id ({client_id}) not found."
        )
    except AccessControlApiException as e:
        raise e


def get_user_site_data(user_id, site_id):
    # API clients require uuid as a string.
    user_id = str(user_id)

    try:
        site_data = settings.USER_DATA_STORE_API.usersitedata_read(str(user_id), site_id)
    except UserDataStoreApiException as e:
        if e.status == 404:
            site_data = create_user_site_data(user_id, site_id)
        else:
            raise e
    return site_data


def get_user_site_role_labels_aggregated(user_id, client_id):
    # Returns a list of sites.
    sites = settings.ACCESS_CONTROL_API.site_list(client_id=client_id)

    # Get the id of the site
    if len(sites) == 1:  # It is not necessary to check if the site is active
        site_id = sites[0].id

        # Return the roles
        return settings.AC_OPERATIONAL_API.get_user_site_role_labels_aggregated(
            str(user_id), site_id).roles
    raise exceptions.ImproperlyConfigured(
        f"Site for client.id ({client_id}) not found."
    )


def get_invitation_data(invitation_id):
    try:
        invitation_data = settings.ACCESS_CONTROL_API.invitation_read(
            invitation_id
        )
    except AccessControlApiException as e:
        return {"error": True, "code": e.status}

    return invitation_data.to_dict()


def invitation_redeem(invitation_id, user_id):
    user_id = str(user_id)
    try:
        redeem_data = settings.ACCESS_CONTROL_API.invitation_redeem(
            invitation_id=invitation_id, user_id=user_id
        )
    except AccessControlApiException as e:
        return {"error": True, "code": e.status}
    return {"error": False}
