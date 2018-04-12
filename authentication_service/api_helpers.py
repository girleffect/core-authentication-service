import json

from django.conf import settings


def get_user_site_data(user_id, site_id):
    return settings.USER_DATA_STORE_APIusersitedata_read(str(user_id), site_id)


def create_user_site_data(user_id, site_id):
    return settings.USER_DATA_STORE_API.usersitedata_create(data={
        "user_id": user_id, "site_id": site_id
    })

def user_site_roles_aggregated(user_id, client_id):
    # Returns a list of sites.
    result = settings.ACCESS_CONTROL_API.site_list(client_id=client_id)

    # Get the id of the site
    site_id = result[0].id

    # Return the roles
    return settings.AC_OPERATIONAL_API.get_user_site_role_labels_aggregated(
        str(user_id), site_id).roles
