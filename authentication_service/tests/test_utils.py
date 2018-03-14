import os

import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase


class APIKeyTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Test data
        cls.user_1 = get_user_model().objects.create(
            username="test_user_1",
            email="",
            is_superuser=1,
            is_staff=1,
            birth_date=datetime.date(2000, 1, 1)
        )
        cls.user_1.set_password("password")
        cls.user_1.save()

        # Set environment variable for testing purposes.
        os.environ["ALLOWED_API_KEYS"] = "oc1choh0rooqu0egae1O"

    def test_unauthorized(self):
        response = self.client.get(
            "/api/v1/clients"
        )
        self.assertEqual(response.status_code, 401)

    def test_forbidden(self):
        response = self.client.get(
            "/api/v1/clients",
            **{"HTTP_X_API_KEY": "notavalidkey"}
        )
        self.assertEqual(response.status_code, 403)

    def test_authorized(self):
        response = self.client.get(
            "/api/v1/clients",
            **{"HTTP_X_API_KEY": "oc1choh0rooqu0egae1O"}
        )
        self.assertEqual(response.status_code, 200)
