import datetime
import json
import jsonschema
import os
import random
import uuid

from oidc_provider.models import Client
from unittest.mock import patch, MagicMock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex

from access_control import Invitation
from authentication_service import models
from authentication_service.api import schemas
from authentication_service.models import UserSite


class IntegrationTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.headers = {"HTTP_X_API_KEY": "test-api-key"}

        # Organisational units
        cls.MAX_ORG_UNITS = 5
        cls.organisations = [
            models.Organisation.objects.create(
                name=f"test_unit_{i}",
                description="Desc"
            )
            for i in range(0, 5)
        ]

        # Create users
        cls.user_1 = get_user_model().objects.create(
            username="test_user_1",
            first_name="Firstname",
            last_name="Lastname",
            email="firstname@example.com",
            is_superuser=1,
            is_staff=1,
            birth_date=datetime.date(2000, 1, 1),
            organisation=cls.organisations[0]
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
        cls.total_countries = 0
        for language in settings.LANGUAGES:
            if not len(language[0]) > 2:
                models.Country.objects.get_or_create(
                    code=language[0], name=language[1]
                )
        cls.total_countries = models.Country.objects.all().count()

    def test_organisation_list(self):
        # Test complete list
        response = self.client.get("/api/v1/organisations", **self.headers)
        self.assertEqual(len(response.json()),
                         min(self.MAX_ORG_UNITS, settings.DEFAULT_LISTING_LIMIT))
        self.assertEqual(int(response["X-Total-Count"]), self.MAX_ORG_UNITS)

        # Test without authorisation
        response = self.client.get("/api/v1/organisations")
        self.assertEqual(response.status_code, 401)

        # Test limit
        response = self.client.get("/api/v1/organisations?limit=1", **self.headers)
        self.assertEqual(len(response.json()), 1)
        self.assertContains(response, "%s" % self.organisations[0].name)
        self.assertEqual(int(response["X-Total-Count"]), self.MAX_ORG_UNITS)

        # Test offset
        response = self.client.get("/api/v1/organisations?offset=1", **self.headers)
        self.assertEqual(len(response.json()),
                         min(self.MAX_ORG_UNITS - 1, settings.DEFAULT_LISTING_LIMIT))
        self.assertContains(response, "%s" % self.organisations[1].name)
        self.assertEqual(int(response["X-Total-Count"]), self.MAX_ORG_UNITS)

        # Test bad request
        response = self.client.get("/api/v1/organisations?limit=500", **self.headers)
        self.assertEqual(response.status_code, 400)

    def test_organisation_create(self):
        # Test Create Endpoint
        response = self.client.post(
            "/api/v1/organisations",
            data=json.dumps({
                "name": "Test Org",
                "description": "Test Description"
            }),
            content_type="application/json",
            **self.headers
        )
        organisation = response.json()
        jsonschema.validate(organisation, schema=schemas.organisation)

        # Test without authorisation
        response = self.client.post(
            "/api/v1/organisations",
            data=json.dumps({
                "name": "Test Org",
                "description": "Test Description"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

        # Test if exists
        response = self.client.get(f"/api/v1/organisations/{organisation['id']}",
                                   **self.headers)
        self.assertContains(response, organisation["name"])

    def test_organisation_delete(self):
        # Create Temporary Organisation
        response = self.client.post(
            "/api/v1/organisations",
            data=json.dumps({
                "name": "Temp Org",
                "description": "Temp Description"
            }),
            content_type="application/json",
            **self.headers
        )
        organisation = response.json()

        # Test without authorisation
        response = self.client.post(
            "/api/v1/organisations",
            data=json.dumps({
                "name": "Temp Org",
                "description": "Temp Description"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)

        # Test Delete Organisation
        response = self.client.delete(f"/api/v1/organisations/{organisation['id']}",
                                      **self.headers)
        self.assertEqual(response.status_code, 200)

        # Double check
        response = self.client.get(f"/api/v1/organisations/{organisation['id']}",
                                   **self.headers)
        self.assertEqual(response.status_code, 404)

        # Test Delete Organisation with user linked.
        response = self.client.delete(f"/api/v1/organisations/{self.organisations[0].id}",
                                      **self.headers)
        self.assertEqual(response.status_code, 400)

    def test_organisation_read(self):
        # Test read
        response = self.client.get(f"/api/v1/organisations/{self.organisations[1].id}",
                                   **self.headers)
        self.assertContains(response, self.organisations[1].name)

        # Validate returned data
        jsonschema.validate(response.json(), schema=schemas.organisation)

        # Test without authorisation
        response = self.client.get(f"/api/v1/organisations/{self.organisations[1].id}")
        self.assertEqual(response.status_code, 401)

        # Test non-existent organisation
        response = self.client.get("/api/v1/organisations/999999", **self.headers)
        self.assertEqual(response.status_code, 404)

    def test_organisation_update(self):
        # Test Update
        response = self.client.put(
            f"/api/v1/organisations/{self.organisations[1].id}",
            data=json.dumps({
                "name": "Changed Name",
                "description": "Changed Description"
            }),
            content_type="application/json",
            **self.headers
        )
        self.assertEqual(response.status_code, 200)
        jsonschema.validate(response.json(), schema=schemas.organisation)

        # Test without authorisation
        response = self.client.put(
            f"/api/v1/organisations/{self.organisations[1].id}",
            data=json.dumps({
                "name": "Changed Name",
                "description": "Changed Description"
            }),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)

        # Double Check
        response = self.client.get(f"/api/v1/organisations/{self.organisations[1].id}",
                                   **self.headers)
        organisation = response.json()
        self.assertEqual(organisation["name"], "Changed Name")
        self.assertEqual(organisation["description"], "Changed Description")

    def test_country_list(self):
        # Test complete list
        response = self.client.get("/api/v1/countries", **self.headers)
        self.assertEqual(len(response.json()),
                         min(self.total_countries, settings.DEFAULT_LISTING_LIMIT))
        self.assertEqual(int(response["X-Total-Count"]), self.total_countries)

        # Test without authorisation
        response = self.client.get("/api/v1/countries")
        self.assertEqual(response.status_code, 401)

        # Test limit
        response = self.client.get("/api/v1/countries?limit=1", **self.headers)
        self.assertEqual(len(response.json()), 1)
        self.assertContains(response, "%s" % settings.LANGUAGES[0][0])
        self.assertEqual(int(response["X-Total-Count"]), self.total_countries)

        # Test offset
        response = self.client.get("/api/v1/countries?offset=1", **self.headers)
        self.assertEqual(len(response.json()),
                         min(self.total_countries, settings.DEFAULT_LISTING_LIMIT))
        self.assertContains(response, "%s" % settings.LANGUAGES[1][0])
        self.assertEqual(int(response["X-Total-Count"]), self.total_countries)

        # Test list using country code
        response = self.client.get("/api/v1/countries?country_codes=de,en", **self.headers)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(int(response["X-Total-Count"]), 2)

        # Test bad request
        response = self.client.get("/api/v1/countries?limit=500", **self.headers)
        self.assertEqual(response.status_code, 400)

    def test_country_read(self):
        # Test read
        response = self.client.get("/api/v1/countries/en", **self.headers)
        self.assertContains(response, "English")

        # Validate returned data
        jsonschema.validate(response.json(), schema=schemas.country)

        # Test without authorisation
        response = self.client.get("/api/v1/countries/en")
        self.assertEqual(response.status_code, 401)

        # Test non-existent country
        response = self.client.get("/api/v1/countries/zz", **self.headers)
        self.assertEqual(response.status_code, 404)

    def test_client_list(self):
        # Test complete list
        response = self.client.get("/api/v1/clients", **self.headers)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(int(response["X-Total-Count"]), 2)

        # Test without authorisation
        response = self.client.get("/api/v1/clients")
        self.assertEqual(response.status_code, 401)

        # Test limit
        response = self.client.get("/api/v1/clients?limit=1", **self.headers)
        self.assertEqual(len(response.json()), 1)
        self.assertContains(response, "%s" % self.client_1.id)
        self.assertEqual(int(response["X-Total-Count"]), 2)

        # Test offset
        response = self.client.get("/api/v1/clients?offset=1", **self.headers)
        self.assertEqual(len(response.json()), 1)
        self.assertContains(response, "%s" % self.client_2.id)
        self.assertEqual(int(response["X-Total-Count"]), 2)

        # Test list using client.id
        response = self.client.get(
            "/api/v1/clients?client_ids=%s,%s" % (
                self.client_1.id, self.client_2.id),
            **self.headers
        )
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(int(response["X-Total-Count"]), 2)

        # Test list using client.client_id
        response = self.client.get(
            "/api/v1/clients?client_token_id=%s" % self.client_1.client_id,
            **self.headers
        )
        self.assertContains(response, "test_client_id_1")
        self.assertEqual(int(response["X-Total-Count"]), 1)

        # Test list using combination
        response = self.client.get(
            "/api/v1/clients?client_ids=%s&client_token_id=%s" % (
                self.client_1.id, self.client_1.client_id),
            **self.headers
        )
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(int(response["X-Total-Count"]), 1)

        # Test bad request
        response = self.client.get("/api/v1/clients?limit=500", **self.headers)
        self.assertEqual(response.status_code, 400)

    def test_client_read(self):
        # Test read
        response = self.client.get(
            "/api/v1/clients/%s" % self.client_1.id, **self.headers)
        self.assertContains(response, "test_client_id_1")

        # Validate returned data
        jsonschema.validate(response.json(), schema=schemas.client)

        # Test without authorisation
        response = self.client.get("/api/v1/clients/%s" % self.client_1.id)
        self.assertEqual(response.status_code, 401)

        # Test non-existent client
        response = self.client.get("/api/v1/clients/1234", **self.headers)
        self.assertEqual(response.status_code, 404)

    def test_user_list(self):
        # Test complete list
        response = self.client.get("/api/v1/users", **self.headers)
        self.assertEqual(len(response.json()), 3)
        self.assertEqual(int(response["X-Total-Count"]), 3)

        # Test without authorisation
        response = self.client.get("/api/v1/users")
        self.assertEqual(response.status_code, 401)

        # Test limit
        response = self.client.get("/api/v1/users?limit=1", **self.headers)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(int(response["X-Total-Count"]), 3)

        # Test offset
        response = self.client.get("/api/v1/users?offset=1", **self.headers)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(int(response["X-Total-Count"]), 3)

        # Test list using email
        response = self.client.get("/api/v1/users?email=test@user.com", **self.headers)
        self.assertContains(response, "test_user_3")
        self.assertEqual(int(response["X-Total-Count"]), 1)

        # Test list using username_prefix
        response = self.client.get("/api/v1/users?username=test", **self.headers)
        self.assertEqual(len(response.json()), 3)
        self.assertEqual(int(response["X-Total-Count"]), 3)

        # Test list using multiple user id's
        response = self.client.get(
            "/api/v1/users?user_ids=%s,%s" % (
                self.user_1.id, self.user_3.id), **self.headers)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(int(response["X-Total-Count"]), 2)

        # Test combination
        response = self.client.get(
            "/api/v1/users?email=%s&username_prefix=test&user_ids=%s" % (
                self.user_3.email, self.user_3.id), **self.headers)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(int(response["X-Total-Count"]), 1)

        # Test bad request
        response = self.client.get("/api/v1/users?limit=500", **self.headers)
        self.assertEqual(response.status_code, 400)

    def test_user_read(self):
        # Test read
        response = self.client.get("/api/v1/users/%s" % self.user_3.id, **self.headers)
        self.assertContains(response, "test_user_3")

        # Validate returned data
        jsonschema.validate(response.json(), schema=schemas.user)

        # Test without authorisation
        response = self.client.get("/api/v1/users/%s" % self.user_3.id)
        self.assertEqual(response.status_code, 401)

        # Test non-existent user
        response = self.client.get("/api/v1/users/%s" % uuid.uuid1(), **self.headers)
        self.assertEqual(response.status_code, 404)

    def test_user_update(self):
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
            data=json.dumps(data),
            **self.headers
        )
        self.assertContains(response, self.user_3.id)

        # Test without authorisation
        response = self.client.put(
            "/api/v1/users/%s" % self.user_3.id,
            data=json.dumps(data),
        )
        self.assertEqual(response.status_code, 401)

        # Get user data
        response = self.client.get("/api/v1/users/%s" % self.user_3.id,
                                   **self.headers)
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
            data=json.dumps(data),
            **self.headers
        )
        self.assertEqual(response.status_code, 404)

    def test_user_delete(self):
        # Test delete
        response = self.client.delete("/api/v1/users/%s" % self.user_2.id, **self.headers)

        response = self.client.get("/api/v1/users", **self.headers)
        self.assertEqual(len(response.json()), 2)

        # Test non-existent user
        response = self.client.delete("/api/v1/users/%s" % self.user_2.id, **self.headers)
        self.assertEqual(response.status_code, 404)

        # Test without authorisation
        response = self.client.delete("/api/v1/users/%s" % self.user_2.id)
        self.assertEqual(response.status_code, 401)

    def test_user_list_filter(self):
        users = []
        for index in range(1, random.randint(12, 20)):
            uuid_val = uuid.uuid4()
            user = get_user_model().objects.create(
                username=f"username_{uuid_val}",
                email=f"{uuid_val}@email.com",
                birth_date=datetime.date(2007, 1, 1)
            )
            users.append((user, uuid_val))

        response = self.client.get("/api/v1/users?username=SerNAme", **self.headers)
        self.assertEqual(len(response.json()), len(users))

        # Test without authorisation
        response = self.client.get("/api/v1/users?username=SerNAme")
        self.assertEqual(response.status_code, 401)

        # Test list on last_name
        count = 0
        for index in range(1, 9):
            count += 1
            user = users[index][0]
            user.last_name = f"mY_last_{index}"
            user.save()
            users[index] = (user, users[index][1])
        response = self.client.get("/api/v1/users?last_name=_lASt_", **self.headers)
        self.assertEqual(len(response.json()), count)

        # Test list on first_name
        count = 0
        for index in range(1, 10):
            count += 1
            user = users[index][0]
            user.first_name = f"mY_first_{index}"
            user.save()
            users[index] = (user, users[index][1])
        response = self.client.get("/api/v1/users?first_name=_fIrsT_", **self.headers)
        self.assertEqual(len(response.json()), count)

        # DOB
        response = self.client.get(
            "/api/v1/users?birth_date="
            '{"from":"2007-01-01T10:44:47.021Z","to":"2018-04-26T10:44:47.021Z]"}',
            **self.headers
        )
        self.assertEqual(len(response.json()), len(users))
        response = self.client.get(
            "/api/v1/users?birth_date="
            '{"from":"2007-01-01","to":"2018-04-26"}',
            **self.headers
        )
        self.assertEqual(len(response.json()), len(users))
        response = self.client.get(
            "/api/v1/users?birth_date="
            '{"from":"2006-01-01T10:44:47.021Z"}',
            **self.headers
        )
        self.assertEqual(len(response.json()), len(users))
        response = self.client.get(
            "/api/v1/users?birth_date="
            '{"to":"1980-01-01T10:44:47.021Z"}',
            **self.headers
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
        response = self.client.get("/api/v1/users?country=de", **self.headers)
        self.assertEqual(len(response.json()), 2)

        # has organisation
        response = self.client.get(
            "/api/v1/users?has_organisation=true", **self.headers)
        self.assertEqual(len(response.json()), 1)
        user = users[0][0]
        user.organisation = self.organisations[1]
        user.save()
        response = self.client.get(
            "/api/v1/users?has_organisation=true", **self.headers)
        self.assertEqual(len(response.json()), 2)

        # organisation
        response = self.client.get(
            f"/api/v1/users?organisation_id={self.organisations[1].id}", **self.headers)
        self.assertEqual(len(response.json()), 1)

        response = self.client.get(
            f"/api/v1/users?tfa_enabled=false", **self.headers)
        self.assertTrue(len(response.json()) > 0)

        totp_device = TOTPDevice.objects.create(
            user=users[0][0],
            name="default",
            confirmed=True,
            key=random_hex().decode()
        )

        response = self.client.get(
            f"/api/v1/users?tfa_enabled=true", **self.headers)
        self.assertEqual(len(response.json()), 1)

        response = self.client.get(
            f"/api/v1/users?site_ids=1,2", **self.headers)
        self.assertEqual(len(response.json()), 0)

        # Link one user to 2 sites
        UserSite.objects.create(user=users[0][0], site_id=1)
        UserSite.objects.create(user=users[0][0], site_id=2)

        response = self.client.get(
            f"/api/v1/users?site_ids=1,2", **self.headers)
        self.assertEqual(int(response["X-Total-Count"]), 1)
        self.assertEqual(len(response.json()), 1)

        # Link another user to site 2
        UserSite.objects.create(user=users[1][0], site_id=2)

        # Querying both sites now results in 2 users...
        response = self.client.get(
            f"/api/v1/users?site_ids=1,2", **self.headers)
        self.assertEqual(int(response["X-Total-Count"]), 2)
        self.assertEqual(len(response.json()), 2)

        # ...while querying only site 1 results in 1 user.
        response = self.client.get(
            f"/api/v1/users?site_ids=1", **self.headers)
        self.assertEqual(len(response.json()), 1)

    def test_user_list_filter_errors(self):
        response = self.client.get(
            "/api/v1/users?birth_date="
            '{"from":null,"to":null}',
            **self.headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content,
                         b"Invalid date range specified: None is not of type 'string'")

        response = self.client.get(
            "/api/v1/users?birth_date="
            '{"from":1,"to":2,"too":3}',
            **self.headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content,
                         b"Invalid date range specified: 1 is not of type 'string'")

        response = self.client.get(
            "/api/v1/users?birth_date="
            '{"from":"2001-01-01","too":"2001-01-01"}',
            **self.headers
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.get(
            "/api/v1/users?birth_date="
            '{"from":"1","to":"2"}',
            **self.headers
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b"Date value(1) does not have correct format: "
                                           b"YYYY-MM-DD or YYYY-MM-DDTHH:MI:SS(.000)Z")

        response = self.client.get(
            "/api/v1/users?birth_date="
            '{"from":"1","to"}',
            **self.headers
        )
        self.assertEqual(response.status_code, 400)

    @override_settings(ACCESS_CONTROL_API=MagicMock(invitation_read=MagicMock()))
    @patch("authentication_service.tasks.send_invitation_email.delay", MagicMock())
    def test_invitation_send(self):
        test_invitation_id = uuid.uuid4()

        settings.ACCESS_CONTROL_API.invitation_read.return_value = Invitation(
            id=test_invitation_id.hex,
            invitor_id=self.user_1.id,  # Valid user
            first_name="Thename",
            last_name="Thesurname",
            email="thename.thesurname@example.com",
            organisation_id=self.organisations[0].id,
            expires_at=timezone.now() + datetime.timedelta(minutes=10),
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

        response = self.client.get(f"/api/v1/invitations/{test_invitation_id}/send",
                                   **self.headers)
        self.assertEqual(response.status_code, 200)

        # Test without authorisation
        response = self.client.get(f"/api/v1/invitations/{test_invitation_id}/send")
        self.assertEqual(response.status_code, 401)

    @override_settings(ACCESS_CONTROL_API=MagicMock(invitation_read=MagicMock()))
    def test_invitation_send_expired(self):
        test_invitation_id = uuid.uuid4()

        settings.ACCESS_CONTROL_API.invitation_read.return_value = Invitation(
            id=test_invitation_id.hex,
            invitor_id=self.user_1.id,  # Valid user
            first_name="Thename",
            last_name="Thesurname",
            email="thename.thesurname@example.com",
            organisation_id=self.organisations[0].id,
            expires_at=timezone.now() - datetime.timedelta(minutes=10),
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

        response = self.client.get(f"/api/v1/invitations/{test_invitation_id}/send",
                                   **self.headers)
        self.assertEqual(response.status_code, 400)

        # Test without authorisation
        response = self.client.get(f"/api/v1/invitations/{test_invitation_id}/send")
        self.assertEqual(response.status_code, 401)

    @override_settings(ACCESS_CONTROL_API=MagicMock(invitation_read=MagicMock()))
    def test_invitation_send_invalid_invitor(self):
        test_invitation_id = uuid.uuid4()

        settings.ACCESS_CONTROL_API.invitation_read.return_value = Invitation(
            id=test_invitation_id.hex,
            invitor_id=uuid.uuid4().hex,
            first_name="Thename",
            last_name="Thesurname",
            email="thename.thesurname@example.com",
            organisation_id=self.organisations[0].id,
            expires_at=timezone.now() + datetime.timedelta(minutes=10),
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

        response = self.client.get(f"/api/v1/invitations/{test_invitation_id}/send",
                                   **self.headers)
        self.assertEqual(response.status_code, 404)

        # Test without authorisation
        response = self.client.get(f"/api/v1/invitations/{test_invitation_id}/send")
        self.assertEqual(response.status_code, 401)

    @override_settings(AC_OPERATIONAL_API=MagicMock(purge_expired_invitations=MagicMock()))
    def test_purge_expired_invitations(self):
        date_string = str(datetime.datetime.now().date())
        # Test without explicit cutoff date
        response = self.client.get("/api/v1/invitations/purge_expired",
                                   **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(settings.AC_OPERATIONAL_API.purge_expired_invitations.called_with(
            date_string
        ))
        # Test with explicit cutoff date
        response = self.client.get(f"/api/v1/invitations/purge_expired?cutoff_date={date_string}",
                                   **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(settings.AC_OPERATIONAL_API.purge_expired_invitations.called_with(
            date_string
        ))
        # Test with malformed cutoff date
        response = self.client.get("/api/v1/invitations/purge_expired?cutoff_date=2019-01-45a",
                                   **self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(settings.AC_OPERATIONAL_API.purge_expired_invitations.called_with(
            date_string
        ))
        # Test with invalid cutoff date
        response = self.client.get("/api/v1/invitations/purge_expired?cutoff_date=2019-01-45",
                                   **self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(settings.AC_OPERATIONAL_API.purge_expired_invitations.called_with(
            date_string
        ))

        # Test without authorisation
        response = self.client.get("/api/v1/invitations/purge_expired")
        self.assertEqual(response.status_code, 401)
