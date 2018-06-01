from django.apps.config import AppConfig
from django.db.models.fields import Field

from authentication_service import lookups


class AuthAppConfig(AppConfig):
    name = "authentication_service"

    def ready(self):
        Field.register_lookup(lookups.Ilike)

