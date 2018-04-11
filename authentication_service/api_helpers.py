from django.conf import settings

import access_control
import user_data_store


def user_site_data(kwargs)
    config = user_data_store.configuration.Configuration(
    api = user_data_store.api.UserDataApi(
        api_client=user_data_store.ApiClient(
            header_name="X-API-KEY",
            header_value=settings.USER_DATA_STORE_API_KEY,
            configuration=config
        )
    )
    result = api.<call_method>(**kwargs)

def user_site_roles_aggregated(kwargs)
    config = access_control.configuration.Configuration(
    api = access_control.api.UserDataApi(
        api_client=access_control.ApiClient(
            header_name="X-API-KEY",
            header_value=settings.ACCESS_CONTROL_API_KEY,
            configuration=config
        )
    )
    result = api.<call_method>(**kwargs)
