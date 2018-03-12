import json
import os

import datetime
import uuid

import jsonschema
from django.contrib.auth import get_user_model
from django.test import TestCase
from oidc_provider.models import Client

from authentication_service.api import schemas


class IntegrationTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Create users
        cls.user_1 = get_user_model().objects.create(
            username="test_user_1",
            email="",
            is_superuser=1,
            is_staff=1,
            birth_date=datetime.date(2000, 1, 1)
        )
        cls.user_1.set_password("password")
        cls.user_1.save()

        cls.user_2 = get_user_model().objects.create(
            username="test_user_2",
            is_superuser=0,
            is_staff=0,
            birth_date=datetime.date(2000, 1, 1)
        )
        cls.user_2.set_password("password")
        cls.user_2.save()

        cls.user_3 = get_user_model().objects.create(
            username="test_user_3",
            email="test@user.com",
            is_superuser=0,
            is_staff=1,
            birth_date=datetime.date(2000, 1, 1)
        )
        cls.user_3.set_password("password")
        cls.user_3.save()

        # Create Clients
        cls.client_1 = Client.objects.create(
            client_id="test_client_id_1",
            name="Wagtail client 1",
            client_secret="super_test_client_secret_1",
            response_type="code",
            jwt_alg="HS256",
            redirect_uris=[
                    os.environ.get("TEST_1_IP", 'http://example.com/')
            ]
        )
        cls.client_2 = Client.objects.create(
            client_id="test_client_id_2",
            name="Wagtail client 2",
            client_secret="super_test_client_secret_2",
            response_type="code",
            jwt_alg="HS256",
            redirect_uris=[
                os.environ.get("TEST_2_IP", 'http://example.com/')
            ]
        )

    def test_client_list(self):
        # Authorize user
        self.client.login(username="test_user_1", password="password")

        # Test complete list
        response = self.client.get("/api/v1/clients")
        self.assertEqual(len(response.json()), 2)

        # Test limit
        response = self.client.get("/api/v1/clients?limit=1")
        self.assertEqual(len(response.json()), 1)
        self.assertContains(response, "%s" % self.client_1.id)

        # Test offset
        response = self.client.get("/api/v1/clients?offset=1")
        self.assertEqual(len(response.json()), 1)
        self.assertContains(response, "%s" % self.client_2.id)

        # Test list using client.id
        response = self.client.get(
            "/api/v1/clients?client_ids=%s&client_ids=%s" % (
                self.client_1.id, self.client_2.id)
        )
        self.assertEqual(len(response.json()), 2)

        # Test list using client.client_id
        response = self.client.get(
            "/api/v1/clients?client_token_id=%s" % self.client_1.client_id
        )
        self.assertContains(response, "test_client_id_1")

        # Test list using combination
        response = self.client.get(
            "/api/v1/clients?client_ids=%s&client_token_id=%s" % (
                self.client_1.id, self.client_1.client_id)
        )
        self.assertEqual(len(response.json()), 1)

        # Test bad request
        response = self.client.get("/api/v1/clients?limit=500")
        self.assertEqual(response.status_code, 400)

        # Test non-existent client
        response = self.client.get("/api/v1/clients?client_ids=1234")
        self.assertEqual(response.status_code, 404)

    def test_client_read(self):
        # Authorize user
        self.client.login(username="test_user_2", password="password")

        # Test read
        response = self.client.get(
            "/api/v1/clients/%s" % self.client_1.client_id)
        self.assertContains(response, "test_client_id_1")

        # Validate returned data
        jsonschema.validate(response.json(), schema=schemas.client)

        # Test non-existent client
        response = self.client.get("/api/v1/clients/1234")
        self.assertEqual(response.status_code, 404)

    def test_user_list(self):
        # Authorize user
        self.client.login(username="test_user_1", password="password")

        # Test complete list
        response = self.client.get("/api/v1/users")
        self.assertEqual(len(response.json()), 3)

        # Test limit
        response = self.client.get("/api/v1/users?limit=1")
        self.assertEqual(len(response.json()), 1)

        # Test offset
        response = self.client.get("/api/v1/users?offset=1")
        self.assertEqual(len(response.json()), 2)

        # Test list using email
        response = self.client.get("/api/v1/users?email=test@user.com")
        self.assertContains(response, "test_user_3")

        # Test list using username_prefix
        response = self.client.get("/api/v1/users?username_prefix=test")
        self.assertEqual(len(response.json()), 3)

        # Test list using multiple user id's
        response = self.client.get(
            "/api/v1/users?user_ids=%s&user_ids=%s" % (
                self.user_1.id, self.user_3.id))
        self.assertEqual(len(response.json()), 2)

        # Test combination
        response = self.client.get(
            "/api/v1/users?email=%s&username_prefix=test&user_ids=%s" % (
                self.user_3.email, self.user_3.id))
        self.assertEqual(len(response.json()), 1)

        # Test bad request
        response = self.client.get("/api/v1/users?limit=500")
        self.assertEqual(response.status_code, 400)

        # Test non-existent user
        response = self.client.get("/api/v1/users?email=not@here.com")
        self.assertEqual(response.status_code, 404)

    def test_user_read(self):
        # Authorize user
        self.client.login(username="test_user_2", password="password")

        # Test read
        response = self.client.get("/api/v1/users/%s" % self.user_3.id)
        self.assertContains(response, "test_user_3")

        # Validate returned data
        jsonschema.validate(response.json(), schema=schemas.user)

        # Test non-existent user
        response = self.client.get("/api/v1/users/%s" % uuid.uuid1())
        self.assertEqual(response.status_code, 404)

    def test_user_update(self):
        # Authorize user
        self.client.login(username="test_user_3", password="password")

        data = {
                "first_name": "Test",
                "last_name": "User",
                "email": "testuser2@tests.com",
                "is_active": True,
                "email_verified": False,
                "msisdn_verified": False,
                "msisdn": "",
                "gender": "",
                "birth_date": "2000-01-01"
            }

        # Test read
        response = self.client.put(
            "/api/v1/users/%s" % self.user_3.id,
            data=json.dumps(data)
        )
        self.assertContains(response, self.user_3.id)

        # Get user data
        response = self.client.get("/api/v1/users/%s" % self.user_3.id)
        user = response.json()

        # Ensure object returned is for the correct user
        self.assertEqual(user["id"], str(self.user_3.id))

        # Check data was updated
        self.assertEqual(user["first_name"], "Test")
        self.assertEqual(user["last_name"], "User")
        self.assertEqual(user["email"], "testuser2@tests.com")

        # Check non-existent user
        response = self.client.put(
            "/api/v1/users/%s" % uuid.uuid1(),
            data=json.dumps(data)
        )
        self.assertEqual(response.status_code, 404)

    def test_user_delete(self):
        # Authorize user
        self.client.login(username="test_user_1", password="password")

        # Test delete
        response = self.client.delete("/api/v1/users/%s" % self.user_2.id)

        response = self.client.get("/api/v1/users")
        self.assertEqual(len(response.json()), 2)

        # Test non-existent user
        response = self.client.delete("/api/v1/users/%s" % self.user_2.id)
        self.assertEqual(response.status_code, 404)
