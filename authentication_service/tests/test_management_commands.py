from unittest import TestCase

from django.core.management import call_command


class TestManagementCommands(TestCase):

    def test_load_security_questions(self):
        # We simply test that the management command executes without any
        # errors.
        call_command("load_security_questions")

    def test_demo_content(self):
        # We simply test that the management command executes without any
        # errors.
        call_command("demo_content", "--no-api-calls")
