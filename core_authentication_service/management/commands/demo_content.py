import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from oidc_provider.models import Client


class Command(BaseCommand):

    def handle(self, *args, **options):
        c = Client(
            name="Wagtail client 1",
            client_id="client_id_1",
            client_secret="super_client_secret_1",
            response_type="code",
            redirect_uris=[
                os.environ.get("WAGTAIL_1_IP",'http://example.com/')
            ]
        )
        c.save()

        # Super user
        user = User.objects.create(username="admin", is_superuser=1, is_staff=1)
        user.set_password("local")
        user.save()
