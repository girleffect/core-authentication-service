import random
import json
import os
import jsonschema
import datetime
import uuid

from oidc_provider.models import Client
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from authentication_service import models
from authentication_service.api import schemas
from authentication_service.models import UserSite


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

        # Create countries
        for language in settings.LANGUAGES:
            if not len(language[0]) > 2:
                models.Country.objects.create(
                    code=language[0], name=language[1]
                )
        # Organisational unit
        cls.org_unit = models.OrganisationalUnit.objects.create(
            name="test_unit",
            description="Desc"
        )

    def test_client_list(self):
        # Authorize user
        self.client.login(username="test_user_1", password="password")

        # Test complete list
        response = self.client.get("/api/v1/clients")
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(int(response["X-Total-Count"]), 2)

        # Test limit
        response = self.client.get("/api/v1/clients?limit=1")
        self.assertEqual(len(response.json()), 1)
        self.assertContains(response, "%s" % self.client_1.id)
        self.assertEqual(int(response["X-Total-Count"]), 2)

        # Test offset
        response = self.client.get("/api/v1/clients?offset=1")
        self.assertEqual(len(response.json()), 1)
        self.assertContains(response, "%s" % self.client_2.id)
        self.assertEqual(int(response["X-Total-Count"]), 2)

        # Test list using client.id
        response = self.client.get(
            "/api/v1/clients?client_ids=%s,%s" % (
                self.client_1.id, self.client_2.id)
        )
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(int(response["X-Total-Count"]), 2)

        # Test list using client.client_id
        response = self.client.get(
            "/api/v1/clients?client_token_id=%s" % self.client_1.client_id
        )
        self.assertContains(response, "test_client_id_1")
        self.assertEqual(int(response["X-Total-Count"]), 1)

        # Test list using combination
        response = self.client.get(
            "/api/v1/clients?client_ids=%s&client_token_id=%s" % (
                self.client_1.id, self.client_1.client_id)
        )
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(int(response["X-Total-Count"]), 1)

        # Test bad request
        response = self.client.get("/api/v1/clients?limit=500")
        self.assertEqual(response.status_code, 400)

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
        self.assertEqual(int(response["X-Total-Count"]), 3)

        # Test limit
        response = self.client.get("/api/v1/users?limit=1")
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(int(response["X-Total-Count"]), 3)

        # Test offset
        response = self.client.get("/api/v1/users?offset=1")
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(int(response["X-Total-Count"]), 3)

        # Test list using email
        response = self.client.get("/api/v1/users?email=test@user.com")
        self.assertContains(response, "test_user_3")
        self.assertEqual(int(response["X-Total-Count"]), 1)

        # Test list using username_prefix
        response = self.client.get("/api/v1/users?username=test")
        self.assertEqual(len(response.json()), 3)
        self.assertEqual(int(response["X-Total-Count"]), 3)

        # Test list using multiple user id's
        response = self.client.get(
            "/api/v1/users?user_ids=%s,%s" % (
                self.user_1.id, self.user_3.id))
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(int(response["X-Total-Count"]), 2)

        # Test combination
        response = self.client.get(
            "/api/v1/users?email=%s&username_prefix=test&user_ids=%s" % (
                self.user_3.email, self.user_3.id))
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(int(response["X-Total-Count"]), 1)

        # Test bad request
        response = self.client.get("/api/v1/users?limit=500")
        self.assertEqual(response.status_code, 400)

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

    def test_user_list_filter(self):
        self.client.login(username="test_user_1", password="password")
        users = []
        for index in range(1, random.randint(12, 20)):
            uuid_val = uuid.uuid4()
            user = get_user_model().objects.create(
                username=f"username_{uuid_val}",
                email=f"{uuid_val}@email.com",
                birth_date=datetime.date(2007, 1, 1)
            )
            users.append((user, uuid_val))

        # Test list using username
        print ("\nusername")
        response = self.client.get("/api/v1/users?username=SerNAme")

        # SQL
        """SELECT "authentication_service_coreuser"."id",
        "authentication_service_coreuser"."username",
        "authentication_service_coreuser"."first_name",
        "authentication_service_coreuser"."last_name",
        "authentication_service_coreuser"."email",
        "authentication_service_coreuser"."is_active",
        "authentication_service_coreuser"."date_joined",
        "authentication_service_coreuser"."last_login",
        "authentication_service_coreuser"."email_verified",
        "authentication_service_coreuser"."msisdn_verified",
        "authentication_service_coreuser"."msisdn",
        "authentication_service_coreuser"."gender",
        "authentication_service_coreuser"."birth_date",
        "authentication_service_coreuser"."avatar",
        "authentication_service_coreuser"."country_id",
        "authentication_service_coreuser"."created_at",
        "authentication_service_coreuser"."updated_at", (COUNT(*) OVER ()) AS
        "x_total_count" FROM "authentication_service_coreuser" WHERE
        "authentication_service_coreuser"."username" ILIKE %SerNAme% ORDER BY
        "authentication_service_coreuser"."id" ASC LIMIT 20"""

        self.assertEqual(len(response.json()), len(users))
        print ("\n" + "-"*20)

        # Test list on last_name
        count = 0
        for index in range(1, 9):
            count += 1
            user = users[index][0]
            user.last_name = f"last_{index}"
            user.save()
            users[index] = (user, users[index][1])
        response = self.client.get("/api/v1/users?last_name=ASt")
        self.assertEqual(len(response.json()), count)

        # Test list on first_name
        count = 0
        for index in range(1, 10):
            count += 1
            user = users[index][0]
            user.first_name = f"first_{index}"
            user.save()
            users[index] = (user, users[index][1])
        response = self.client.get("/api/v1/users?first_name=IrsT")
        self.assertEqual(len(response.json()), count)

        # DOB
        response = self.client.get(
            "/api/v1/users?birth_date="
            '{"from":"2007-01-01T10:44:47.021Z","to":"2018-04-26T10:44:47.021Z]"}'
        )
        self.assertEqual(len(response.json()), len(users))
        response = self.client.get(
            "/api/v1/users?birth_date="
            '{"from":"2007-01-01","to":"2018-04-26"}'
        )
        self.assertEqual(len(response.json()), len(users))
        response = self.client.get(
            "/api/v1/users?birth_date="
            '{"from":"2006-01-01T10:44:47.021Z"}'
        )
        self.assertEqual(len(response.json()), len(users))
        response = self.client.get(
            "/api/v1/users?birth_date="
            '{"to":"1980-01-01T10:44:47.021Z"}'
        )
        self.assertEqual(len(response.json()), 0)

        # Country
        user = users[0][0]
        user.country = models.Country.objects.get(code="de")
        user.save()
        users[0] = (user, users[0][1])
        user = users[3][0]
        user.country = models.Country.objects.get(code="de")
        user.save()
        users[3] = (user, users[3][1])
        response = self.client.get("/api/v1/users?country=de")
        self.assertEqual(len(response.json()), 2)

        # has organisational unit
        response = self.client.get(
            "/api/v1/users?has_organisational_unit=true")
        self.assertEqual(len(response.json()), 0)
        user = users[0][0]
        user.organisational_unit = self.org_unit
        user.save()
        response = self.client.get(
            "/api/v1/users?has_organisational_unit=true")
        self.assertEqual(len(response.json()), 1)

        # organisational_unit
        response = self.client.get(
            f"/api/v1/users?organisational_unit_id={self.org_unit.id}")
        self.assertEqual(len(response.json()), 1)

        response = self.client.get(
            f"/api/v1/users?tfa_enabled=false")
        self.assertTrue(len(response.json()) > 0)

        totp_device = TOTPDevice.objects.create(
            user=users[0][0],
            name="default",
            confirmed=True,
            key=random_hex().decode()
        )

        response = self.client.get(
            f"/api/v1/users?tfa_enabled=true")
        self.assertEqual(len(response.json()), 1)

        response = self.client.get(
            f"/api/v1/users?site_ids=1,2")
        self.assertEqual(len(response.json()), 0)

        # Link one user to 2 sites
        UserSite.objects.create(user=users[0][0], site_id=1)
        UserSite.objects.create(user=users[0][0], site_id=2)

        response = self.client.get(
            f"/api/v1/users?site_ids=1,2")
        print(response.json())
        self.assertEqual(len(response.json()), 1)

        # Link another user to site 2
        UserSite.objects.create(user=users[1][0], site_id=2)

        # Querying both sites now results in 2 users...
        response = self.client.get(
            f"/api/v1/users?site_ids=1,2")
        self.assertEqual(len(response.json()), 2)

        # ...while querying only site 1 results in 1 user.
        response = self.client.get(
            f"/api/v1/users?site_ids=1")
        self.assertEqual(len(response.json()), 1)


    def test_user_list_filter_errors(self):
        self.client.login(username="test_user_3", password="password")
        response = self.client.get(
            "/api/v1/users?birth_date="
            '{"from":null,"to":null}'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b"Date range object does not contain any date object values")

        response = self.client.get(
            "/api/v1/users?birth_date="
            '{"from":1,"to":2,"too":3}'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b"Date range object with length:3, exceeds max length of 2")

        response = self.client.get(
            "/api/v1/users?birth_date="
            '{"from":null,"to":null,"too":null}'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b"Date range object with length:3, exceeds max length of 2")

        response = self.client.get(
            "/api/v1/users?birth_date="
            '{"from":"1","to":"2"}'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b"Date value(1) does not have correct format YYYY-MM-DD")

        response = self.client.get(
            "/api/v1/users?birth_date="
            '{"from":"1","to"}'
        )
        self.assertEqual(response.status_code, 400)
