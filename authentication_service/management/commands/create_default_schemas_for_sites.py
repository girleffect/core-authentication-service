from django.conf import settings
from django.core.management.base import BaseCommand

from user_data_store.rest import ApiException


class Command(BaseCommand):
    help = "Create all SiteDataSchemas for all sites found on Access Control."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Creating SiteDataSchemas..."))
        sites = settings.ACCESS_CONTROL_API.site_list()
        if sites:
            for site in sites:
                try:
                    schemas = settings.USER_DATA_STORE_API.sitedataschema_list(site_id=site.id)
                    if not schemas:
                        self.stdout.write(
                            self.style.SUCCESS("Creating Schema for site %s..." % site.name)
                        )
                        settings.USER_DATA_STORE_API.sitedataschema_create(
                            data={
                                "site_id": site.id,
                                "schema": {"type": "object"}
                            }
                        )
                    else:
                        self.stdout.write(
                            self.style.SUCCESS("Schema for site %s exists!" % site.name)
                        )
                except ApiException as e:
                    raise e

        else:
            self.stdout.write(self.style.SUCCESS("No sites found on Access Control!"))
