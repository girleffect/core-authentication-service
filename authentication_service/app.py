from django.apps.config import AppConfig
from django.db.models.fields import Field

from authentication_service import lookups


class AuthAppConfig(AppConfig):
    name = "authentication_service"

    def ready(self):
        # We have to import signals only when the app is ready.
        from authentication_service import signals
        Field.register_lookup(lookups.Ilike)

