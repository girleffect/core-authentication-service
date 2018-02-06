import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from authentication_service.models import SecurityQuestion

SECURITY_QUESTIONS = [
    {
        "id": 1,
        "question_text": "What is your favourite colour?",
        "translations": []
    },
    {
        "id": 2,
        "question_text": "What is your mother's maiden name?",
        "translations": []
    },
]


class Command(BaseCommand):
    help = "Create an initial list of security questions"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Loading security questions.."))
        for question_detail in SECURITY_QUESTIONS:
            security_question, created = \
                SecurityQuestion.objects.update_or_create(
                    id=question_detail["id"],
                    defaults={
                        "question_text": question_detail["question_text"]
                    }
                )
            security_question.save()
            operation = "Created" if created else "Updated"
            msg = "{} security question {}: {}".format(
                operation, security_question.id, security_question.question_text
            )
            self.stdout.write(self.style.SUCCESS(msg))

        self.stdout.write(self.style.SUCCESS("Done."))
