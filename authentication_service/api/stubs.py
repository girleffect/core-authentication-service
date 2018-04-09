"""
Do not modify this file. It is generated from the Swagger specification.
"""
import json
from apitools.datagenerator import DataGenerator

import authentication_service.api.schemas as schemas


class AbstractStubClass(object):
    """
    Implementations need to be derived from this class.
    """

    @staticmethod
    def client_list(request, offset=None, client_ids=None, client_token_id=None, limit=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        """
        raise NotImplementedError()

    @staticmethod
    def client_read(request, client_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param client_id: string A string value identifying the client
        """
        raise NotImplementedError()

    @staticmethod
    def user_list(request, username_prefix=None, offset=None, email=None, user_ids=None, limit=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        """
        raise NotImplementedError()

    @staticmethod
    def user_delete(request, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        raise NotImplementedError()

    @staticmethod
    def user_read(request, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        raise NotImplementedError()

    @staticmethod
    def user_update(request, body, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param body: dict A dictionary containing the parsed and validated body
        :param user_id: string A UUID value identifying the user.
        """
        raise NotImplementedError()


class MockedStubClass(AbstractStubClass):
    """
    Provides a mocked implementation of the AbstractStubClass.
    """
    GENERATOR = DataGenerator()

    @staticmethod
    def client_list(request, offset=None, client_ids=None, client_token_id=None, limit=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        """
        response_schema = json.loads("""{
    "items": {
        "properties": {
            "_post_logout_redirect_uris": {
                "description": "New-line delimited list of post-logout redirect URIs",
                "type": "string"
            },
            "_redirect_uris": {
                "description": "New-line delimited list of redirect URIs",
                "type": "string"
            },
            "client_id": {
                "description": "",
                "type": "string"
            },
            "contact_email": {
                "description": "",
                "type": "string"
            },
            "id": {
                "description": "",
                "type": "integer"
            },
            "logo": {
                "description": "",
                "format": "uri",
                "type": "string"
            },
            "name": {
                "description": "",
                "type": "string"
            },
            "require_consent": {
                "description": "If disabled, the Server will NEVER ask the user for consent.",
                "type": "boolean"
            },
            "response_type": {
                "description": "",
                "type": "string"
            },
            "reuse_consent": {
                "description": "If enabled, the Server will save the user consent given to a specific client, so that user won't be prompted for the same authorization multiple times.",
                "type": "boolean"
            },
            "terms_url": {
                "description": "External reference to the privacy policy of the client.",
                "type": "string"
            },
            "website_url": {
                "description": "",
                "type": "string"
            }
        },
        "required": [
            "id",
            "client_id",
            "response_type"
        ],
        "type": "object",
        "x-scope": [
            ""
        ]
    },
    "type": "array"
}""")
        if "type" not in response_schema:
            response_schema["type"] = "object"

        if response_schema["type"] == "array" and "type" not in response_schema["items"]:
            response_schema["items"]["type"] = "object"

        return MockedStubClass.GENERATOR.random_value(response_schema)

    @staticmethod
    def client_read(request, client_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param client_id: string A string value identifying the client
        """
        response_schema = schemas.client
        if "type" not in response_schema:
            response_schema["type"] = "object"

        if response_schema["type"] == "array" and "type" not in response_schema["items"]:
            response_schema["items"]["type"] = "object"

        return MockedStubClass.GENERATOR.random_value(response_schema)

    @staticmethod
    def user_list(request, username_prefix=None, offset=None, email=None, user_ids=None, limit=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        """
        response_schema = json.loads("""{
    "items": {
        "properties": {
            "avatar": {
                "format": "uri",
                "type": "string"
            },
            "birth_date": {
                "format": "date",
                "type": "string"
            },
            "country_code": {
                "maxLength": 2,
                "minLength": 2,
                "type": "string"
            },
            "created_at": {
                "format": "date-time",
                "readOnly": true,
                "type": "string"
            },
            "date_joined": {
                "description": "",
                "format": "date",
                "readOnly": true,
                "type": "string"
            },
            "email": {
                "description": "",
                "format": "email",
                "type": "string"
            },
            "email_verified": {
                "type": "boolean"
            },
            "first_name": {
                "description": "",
                "type": "string"
            },
            "gender": {
                "type": "string"
            },
            "id": {
                "description": "A UUID identifying the user",
                "format": "uuid",
                "readOnly": true,
                "type": "string"
            },
            "is_active": {
                "description": "Designates whether this user should be treated as active. Deselect this instead of deleting accounts.",
                "type": "boolean"
            },
            "last_login": {
                "description": "",
                "format": "date-time",
                "readOnly": true,
                "type": "string"
            },
            "last_name": {
                "description": "",
                "type": "string"
            },
            "msisdn": {
                "maxLength": 15,
                "type": "string"
            },
            "msisdn_verified": {
                "type": "boolean"
            },
            "updated_at": {
                "format": "date-time",
                "readOnly": true,
                "type": "string"
            },
            "username": {
                "description": "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                "readOnly": true,
                "type": "string"
            }
        },
        "required": [
            "id",
            "username",
            "is_active",
            "date_joined",
            "created_at",
            "updated_at"
        ],
        "type": "object",
        "x-scope": [
            ""
        ]
    },
    "type": "array"
}""")
        if "type" not in response_schema:
            response_schema["type"] = "object"

        if response_schema["type"] == "array" and "type" not in response_schema["items"]:
            response_schema["items"]["type"] = "object"

        return MockedStubClass.GENERATOR.random_value(response_schema)

    @staticmethod
    def user_delete(request, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        response_schema = schemas.__UNSPECIFIED__
        if "type" not in response_schema:
            response_schema["type"] = "object"

        if response_schema["type"] == "array" and "type" not in response_schema["items"]:
            response_schema["items"]["type"] = "object"

        return MockedStubClass.GENERATOR.random_value(response_schema)

    @staticmethod
    def user_read(request, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        response_schema = schemas.user
        if "type" not in response_schema:
            response_schema["type"] = "object"

        if response_schema["type"] == "array" and "type" not in response_schema["items"]:
            response_schema["items"]["type"] = "object"

        return MockedStubClass.GENERATOR.random_value(response_schema)

    @staticmethod
    def user_update(request, body, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param body: dict A dictionary containing the parsed and validated body
        :param user_id: string A UUID value identifying the user.
        """
        response_schema = schemas.user
        if "type" not in response_schema:
            response_schema["type"] = "object"

        if response_schema["type"] == "array" and "type" not in response_schema["items"]:
            response_schema["items"]["type"] = "object"

        return MockedStubClass.GENERATOR.random_value(response_schema)
