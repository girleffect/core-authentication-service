import logging

from django.conf import settings

LOGGER = logging.getLogger(__name__)


def get_user_site_data(user_id, client_id):
    # API clients require uuid as a string.
    user_id = str(user_id)

    # Get the site. Client id is unique on access-control
    sites = settings.ACCESS_CONTROL_API.site_list(client_id=client_id)
    if len(sites) > 0:
        site = sites[0]
        site_data = settings.USER_DATA_STORE_API.usersitedata_read(str(user_id), client_id)
        # TODO if it does not exist, create.
        return site_data
    LOGGER.error(f"Site for client.id ({client_id}) not found")


def create_user_site_data(user_id, client_id):
    return settings.USER_DATA_STORE_API.usersitedata_create(data={
        "user_id": user_id, "site_id": client_id
    })

def user_site_roles_aggregated(user_id, client_id):
    # Returns a list of sites.
    result = settings.ACCESS_CONTROL_API.site_list(client_id=client_id)

    # Get the id of the site
    site_id = result[0].id

    # Return the roles
    return settings.AC_OPERATIONAL_API.get_user_site_role_labels_aggregated(
        str(user_id), site_id).roles
