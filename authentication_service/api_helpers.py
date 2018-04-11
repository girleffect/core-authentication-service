from django.conf import settings

import access_control
import user_data_store


def get_user_site_data(user_id, site_id):
    config = user_data_store.configuration.Configuration()
    api = user_data_store.api.UserDataApi(
        api_client=user_data_store.ApiClient(
            header_name="X-API-KEY",
            header_value=settings.USER_DATA_STORE_API_KEY,
            configuration=config
        )
    )
    result = api.usersitedata_read(user_id, site_id)

def create_user_site_data(user_id, site_id):
    config = user_data_store.configuration.Configuration()
    api = user_data_store.api.UserDataApi(
        api_client=user_data_store.ApiClient(
            header_name="X-API-KEY",
            header_value=settings.USER_DATA_STORE_API_KEY,
            configuration=config
        )
    )
    result = api.usersitedata_create(data={
        "user_id": user_id, "site_id": site_id
    })

def user_site_roles_aggregated(user_id, site_id):
    config = access_control.configuration.Configuration()
    api = access_control.api.OperationalApi(
        api_client=access_control.ApiClient(
            header_name="X-API-KEY",
            header_value=settings.ACCESS_CONTROL_API_KEY,
            configuration=config
        )
    )
    return api.get_user_site_role_labels_aggregated(str(user_id), site_id)
