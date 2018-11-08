from django.apps.config import AppConfig
from django.db.models.fields import Field

from authentication_service import lookups

from django.conf import settings

# Import to ensure kinesis producer gets instantiated
#from ge_event_log import events


class AuthAppConfig(AppConfig):
    name = "authentication_service"

    def ready(self):
        # We have to import signals only when the app is ready.
        from authentication_service import signals
        Field.register_lookup(lookups.Ilike)
        from authentication_service import integration, metrics
        metrics.add_prometheus_metrics_for_class(integration.Implementation)
