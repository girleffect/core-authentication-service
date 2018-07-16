from django.core.management.base import BaseCommand

from authentication_service.models import Organisation

ORGANISATIONS = [
    ("Girl Effect", "The Girl Effect Organisation"),
    ("praekelt.com", "Praekelt Consulting"),
    ("praekelt.org", "The Praekelt Foundation")
]


class Command(BaseCommand):
    help = "Create all organisations"

    def handle(self, *args, **options):
        for name, description in ORGANISATIONS:
            self.stdout.write(self.style.SUCCESS("Adding organisation '%s'" % name))
            organisation, created = Organisation.objects.update_or_create(
                name=name, defaults={"description": description}
            )
            self.stdout.write(self.style.SUCCESS("Organisation '{}' {}".format(
                name, "created" if created else "updated"
            )))
