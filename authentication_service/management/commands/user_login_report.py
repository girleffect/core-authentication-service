import argparse
import csv
import datetime
import io

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.core.validators import validate_email
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives

from dateutil.relativedelta import relativedelta


def date_range(string):
    values = string.strip().split(",")

    # Ensure a comma is present, we need to ensure the start and end
    if len(values) != 2:
        msg = (f"{string};"
            " could not be split correctly, please ensure ',' is present."
        )
        raise argparse.ArgumentTypeError(msg)
    try:
        start = datetime.datetime.strptime(
            values[0], "%Y/%m/%d"
        ).date() if values[0] != "*" else None
    except ValueError as e:
        msg = f"{values[0]}; Does not match the format yyyy/mm/dd."
        raise argparse.ArgumentTypeError(msg)
    try:
        end = datetime.datetime.strptime(
            values[1], "%Y/%m/%d"
        ).date() if values[1] != "*" else None
    except ValueError as e:
        msg = f"{values[1]}; Does not match the format yyyy/mm/dd."
        raise argparse.ArgumentTypeError(msg)
    value = [start, end]
    return value


def email(string):
    try:
        validate_email(string)
    except ValidationError:
        raise argparse.ArgumentTypeError(
            f"{string} does not seem to be a valid email address."
        )
    return string


class Command(BaseCommand):
    help = "Mail a csv containing user login for the specified time range."

    def add_arguments(self, parser):
        parser.add_argument(
            "--user-status",
            choices=["both", "active", "inactive"],
            default="both",
            help="Account status for users to include.",
        )
        parser.add_argument(
            "--additional-email",
            type=email,
            help="Adds an extra email to the recipient list.",
        )

        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "-d", "--days",
            type=int,
            help="Relative days since today."
        )
        group.add_argument(
            "-w", "--weeks",
            type=int,
            help="Relative weeks since today."
        )
        group.add_argument(
            "-m", "--months",
            type=int,
            help="Relative months since today."
        )
        group.add_argument(
            "-r", "--range",
            type=date_range,
            help=("Date range in format <start>,<end>; yyyy/mm/dd,yyyy/mm/dd."
                " Everything before a date: *,yyyy/mm/dd."
                " Everything after a date till today: yyyy/mmm/dd,*"
            )
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Fetching users..."))
        self.stdout.write(self.style.SUCCESS(f"{options}"))
        user_model = get_user_model()

        filter_kwargs = {}
        # Add date filters for last login
        if options.get("range") is not None:
            date_range = options["range"]
            if date_range[0]:
                filter_kwargs["last_login__date__gte"] = date_range[0]
            if date_range[1]:
                filter_kwargs["last_login__date__lte"] = date_range[1]
        elif options.get("months") is not None:
            filter_kwargs["last_login__date__gte"] = timezone.now() - relativedelta(months=options["months"])
        elif options.get("weeks") is not None:
            filter_kwargs["last_login__date__gte"] = timezone.now() - relativedelta(weeks=options["weeks"])
        elif options.get("days") is not None:
            filter_kwargs["last_login__date__gte"] = timezone.now() - relativedelta(days=options["days"])

        # Add filter for active flag
        if options.get("user_status") != "both":
            flag = True if options["user_status"] == "active" else False
            filter_kwargs["is_active"] = flag

        # Filter the users
        users = user_model.objects.filter(
            **{k: v for k, v in filter_kwargs.items()}
        )
        print (users)

        file = io.StringIO()
        fields = ["id", "username", "email", "last_login", "created_at", "updated_at"]
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for user in users:
            row = {}
            for field in fields:
                row[field] = getattr(user, field)
            writer.writerow(row)
        message = EmailMultiAlternatives(
            subject="Requested user login data",
            body="",
            from_email="auth@gehosting.org",
            to=["mothershipmaiosl@gmail.com"],  # Must be a list
        )
        message.attach("user.csv",file.getvalue(), "text/csv")
        message.send()
