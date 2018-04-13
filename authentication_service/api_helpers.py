import logging

from django.conf import settings

from user_data_store.rest import ApiException

LOGGER = logging.getLogger(__name__)


def create_user_site_data(user_id, site_id):
    return settings.USER_DATA_STORE_API.usersitedata_create(data={
        "user_id": user_id, "site_id": site_id, "data": {}
    })


def get_user_site_data(user_id, client_id):
    # API clients require uuid as a string.
    user_id = str(user_id)

    # Get the site. Client id is unique on access-control
    sites = settings.ACCESS_CONTROL_API.site_list(client_id=client_id)
    if len(sites) > 0 and sites[0].is_active:
        site_id = sites[0].id
        try:
            site_data = settings.USER_DATA_STORE_API.usersitedata_read(str(user_id), site_id)
        except ApiException as e:
            if e.status == 404:
                site_data = create_user_site_data(user_id, site_id)
            else:
                raise e
        return site_data
    LOGGER.error(f"Site for client.id ({client_id}) not found, or inactive")


def get_user_site_role_labels_aggregated(user_id, client_id):
    # Returns a list of sites.
    result = settings.ACCESS_CONTROL_API.site_list(client_id=client_id)

    # Get the id of the site
    site_id = result[0].id

    # Return the roles
    return settings.AC_OPERATIONAL_API.get_user_site_role_labels_aggregated(
        str(user_id), site_id).roles
