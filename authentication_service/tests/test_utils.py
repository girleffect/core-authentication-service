import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import SuspiciousOperation
from django.test import TestCase

from authentication_service import utils, exceptions


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

    def test_unauthorized(self):
        response = self.client.get(
            "/api/v1/clients"
        )
        self.assertEqual(response.status_code, 401)

    def test_wrong_key(self):
        response = self.client.get(
            "/api/v1/clients",
            **{"HTTP_X_API_KEY": "notavalidkey"}
        )
        self.assertEqual(response.status_code, 401)

    def test_authorized(self):
        response = self.client.get(
            "/api/v1/clients",
            **{"HTTP_X_API_KEY": "test_api_key"}
        )
        self.assertEqual(response.status_code, 200)

    def test_other_key(self):
        response = self.client.get(
            "/api/v1/clients",
            **{"HTTP_X_API_KEY": "some_other_api_key"}
        )
        self.assertEqual(response.status_code, 200)


class DateFilterTestCase(TestCase):

    def test_string_range(self):
        value = utils.range_filter_parser(
            '{"from":"2007-01-01T10:44:47.021Z","to":"2018-04-26T10:44:47.021Z"}')
        self.assertEqual(
            value,
            ("range", [
                datetime.datetime(2007, 1, 1, 10, 44, 47),
                datetime.datetime(2018, 4, 26, 10, 44, 47)
            ])
        )
        value = utils.range_filter_parser('{"from":"2007-01-01","to":"2018-04-26"}')
        self.assertEqual(
            value,
            ("range", [
                datetime.datetime(2007, 1, 1, 0, 0),
                datetime.datetime(2018, 4, 26, 0, 0)
            ])
        )
        value = utils.range_filter_parser(
            '{"from":"2007-01-01T10:44:47.021Z"}')
        self.assertEqual(
            value,
            ("gte", datetime.datetime(2007, 1, 1, 10, 44, 47))
        )
        value = utils.range_filter_parser(
            '{"to":"2018-04-26"}')
        self.assertEqual(
            value,
            ("lte", datetime.datetime(2018, 4, 26, 0, 0))
        )
        value = utils.range_filter_parser(
            '{"from":"2007-01-01","to":"2018-04-26T10:44:47.021Z"}')
        self.assertEqual(
            value,
            ("range", [
                datetime.datetime(2007, 1, 1, 0, 0),
                datetime.datetime(2018, 4, 26, 10, 44, 47)
            ])
        )

    def test_list_range(self):
        value = utils.range_filter_parser(
            {
                "from": datetime.date(2007, 1, 1),
                "to": datetime.date(2018, 1, 26)
            }
        )
        self.assertEqual(
            value,
            ("range", [datetime.date(2007, 1, 1), datetime.date(2018, 1, 26)])
        )
        value = utils.range_filter_parser({
            "from": datetime.datetime(2007, 1, 1, 5, 20, 10),
            "to": datetime.datetime(2018, 1, 26, 5, 20, 10)
        })
        self.assertEqual(
            value,
            ("range", [
                datetime.datetime(2007, 1, 1, 5, 20, 10),
                datetime.datetime(2018, 1, 26, 5, 20, 10)
            ])
        )
        value = utils.range_filter_parser(
            {"from": datetime.date(2007, 1, 1)})
        self.assertEqual(
            value,
            ("gte", datetime.date(2007, 1, 1))
        )
        value = utils.range_filter_parser(
            {"to": datetime.date(2018, 1, 26)})
        self.assertEqual(
            value,
            ("lte", datetime.date(2018, 1, 26))
        )
        value = utils.range_filter_parser({
            "from": datetime.date(2007, 1, 1),
            "to": datetime.datetime(2018, 1, 26, 5, 20, 10)
        })
        self.assertEqual(
            value,
            ("range", [
                datetime.date(2007, 1, 1),
                datetime.datetime(2018, 1, 26, 5, 20, 10)
            ])
        )

    def test_error_list_range(self):
        with self.assertRaises(exceptions.BadRequestException) as e:
            value = utils.range_filter_parser({
                "from": 1,
                "to": 2,
                "too": 3
            })
            self.assertEqual(
                e.message,
                "Date range object with length:3, exceeds max length of 2"
            )

        with self.assertRaises(exceptions.BadRequestException) as e:
            value = utils.range_filter_parser({
                "from": None,
                "to": None,
                "too": None
            })
            self.assertEqual(
                e.message,
                "Date range object with length:3, exceeds max length of 2"
            )

        with self.assertRaises(exceptions.BadRequestException) as e:
            value = utils.range_filter_parser({
                "from": None,
                "to": None
            })
            self.assertEqual(
                e.message,
                "Date range object does not contain any date object values"
            )

        with self.assertRaises(exceptions.BadRequestException) as e:
            value = utils.range_filter_parser([1, 2, 3])
            self.assertEqual(
                e.message,
                "Date range not an object or JSON string."
            )

        with self.assertRaises(exceptions.BadRequestException) as e:
            value = utils.range_filter_parser('{"from":null,"to":null,"too":null}')
            self.assertEqual(
                e.message,
                "Date range object with length:3, exceeds max length of 2"
            )

        with self.assertRaises(exceptions.BadRequestException) as e:
            value = utils.range_filter_parser('{"from":1,"to":2,"too":3}')
            self.assertEqual(
                e.message,
                "Date range object with length:3, exceeds max length of 2"
            )

        with self.assertRaises(exceptions.BadRequestException) as e:
            value = utils.range_filter_parser('{"from":"1","to":"2"}')
            self.assertEqual(
                e.message,
                "Date value(1) does not have correct format YYYY-MM-DD"
            )
