from django.conf import settings
from django.core.management.base import BaseCommand

from user_data_store.rest import ApiException


class Command(BaseCommand):
    help = "Create all SiteDataSchemas for all sites found on Access Control."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Creating SiteDataSchemas..."))
        # Fetch all sites until X-Total-Count is reached.
        done = False
        sites = []
        while not done:
            response = settings.ACCESS_CONTROL_API.site_list_with_http_info(limit=100)
            sites.extend(response[0])
            if len(sites) >= int(response[2]["X-Total-Count"]):
                done = True
        if sites:
            for site in sites:
                try:
                    settings.USER_DATA_STORE_API.sitedataschema_read(site_id=site.id)
                    self.stdout.write(
                        self.style.SUCCESS("Schema for site %s exists!" % site.name)
                    )
                except ApiException as e:
                    if e.status == 404:
                        self.stdout.write(
                            self.style.SUCCESS("Creating Schema for site %s..." % site.name)
                        )
                        settings.USER_DATA_STORE_API.sitedataschema_create(
                            data={
                                "site_id": site.id,
                                "schema": {"type": "object"}
                            }
                        )
                        self.stdout.write(
                            self.style.SUCCESS("Created schema for %s...") % site.name)
                    else:
                        raise

        else:
            self.stdout.write(self.style.SUCCESS("No sites found on Access Control!"))
