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

    # client_list -- Synchronisation point for meld
    @staticmethod
    def client_list(request, offset=None, limit=None, client_ids=None, client_token_id=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        """
        raise NotImplementedError()

    # client_read -- Synchronisation point for meld
    @staticmethod
    def client_read(request, client_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param client_id: string A string value identifying the client
        """
        raise NotImplementedError()

    # country_list -- Synchronisation point for meld
    @staticmethod
    def country_list(request, offset=None, limit=None, country_codes=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        """
        raise NotImplementedError()

    # country_read -- Synchronisation point for meld
    @staticmethod
    def country_read(request, country_code, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param country_code: string A string value identifying the country
        """
        raise NotImplementedError()

    # invitation_send -- Synchronisation point for meld
    @staticmethod
    def invitation_send(request, invitation_id, language=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param invitation_id: string 
        """
        raise NotImplementedError()

    # purge_expired_invitations -- Synchronisation point for meld
    @staticmethod
    def purge_expired_invitations(request, cutoff_date=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        """
        raise NotImplementedError()

    # organisation_list -- Synchronisation point for meld
    @staticmethod
    def organisation_list(request, offset=None, limit=None, organisation_ids=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        """
        raise NotImplementedError()

    # organisation_read -- Synchronisation point for meld
    @staticmethod
    def organisation_read(request, organisation_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param organisation_id: integer An integer identifying an organisation a user belongs to
        """
        raise NotImplementedError()

    # user_list -- Synchronisation point for meld
    @staticmethod
    def user_list(request, offset=None, limit=None, birth_date=None, country=None, date_joined=None, email=None, email_verified=None, first_name=None, gender=None, is_active=None, last_login=None, last_name=None, msisdn=None, msisdn_verified=None, nickname=None, organisation_id=None, updated_at=None, username=None, q=None, tfa_enabled=None, has_organisation=None, order_by=None, user_ids=None, site_ids=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        """
        raise NotImplementedError()

    # user_delete -- Synchronisation point for meld
    @staticmethod
    def user_delete(request, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        raise NotImplementedError()

    # user_read -- Synchronisation point for meld
    @staticmethod
    def user_read(request, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        raise NotImplementedError()

    # user_update -- Synchronisation point for meld
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
    def client_list(request, offset=None, limit=None, client_ids=None, client_token_id=None, *args, **kwargs):
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
    def country_list(request, offset=None, limit=None, country_codes=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        """
        response_schema = json.loads("""{
    "items": {
        "properties": {
            "code": {
                "maxLength": 2,
                "minLength": 2,
                "type": "string"
            },
            "name": {
                "maxLength": 100,
                "type": "string"
            }
        },
        "required": [
            "code",
            "name"
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
    def country_read(request, country_code, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param country_code: string A string value identifying the country
        """
        response_schema = schemas.country
        if "type" not in response_schema:
            response_schema["type"] = "object"

        if response_schema["type"] == "array" and "type" not in response_schema["items"]:
            response_schema["items"]["type"] = "object"

        return MockedStubClass.GENERATOR.random_value(response_schema)

    @staticmethod
    def invitation_send(request, invitation_id, language=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param invitation_id: string 
        """
        response_schema = schemas.__UNSPECIFIED__
        if "type" not in response_schema:
            response_schema["type"] = "object"

        if response_schema["type"] == "array" and "type" not in response_schema["items"]:
            response_schema["items"]["type"] = "object"

        return MockedStubClass.GENERATOR.random_value(response_schema)

    @staticmethod
    def purge_expired_invitations(request, cutoff_date=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        """
        response_schema = schemas.__UNSPECIFIED__
        if "type" not in response_schema:
            response_schema["type"] = "object"

        if response_schema["type"] == "array" and "type" not in response_schema["items"]:
            response_schema["items"]["type"] = "object"

        return MockedStubClass.GENERATOR.random_value(response_schema)

    @staticmethod
    def organisation_list(request, offset=None, limit=None, organisation_ids=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        """
        response_schema = json.loads("""{
    "items": {
        "properties": {
            "created_at": {
                "format": "date-time",
                "readOnly": true,
                "type": "string"
            },
            "description": {
                "type": "string"
            },
            "id": {
                "type": "integer"
            },
            "name": {
                "type": "string"
            },
            "updated_at": {
                "format": "date-time",
                "readOnly": true,
                "type": "string"
            }
        },
        "required": [
            "id",
            "name",
            "description",
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
    def organisation_read(request, organisation_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param organisation_id: integer An integer identifying an organisation a user belongs to
        """
        response_schema = schemas.organisation
        if "type" not in response_schema:
            response_schema["type"] = "object"

        if response_schema["type"] == "array" and "type" not in response_schema["items"]:
            response_schema["items"]["type"] = "object"

        return MockedStubClass.GENERATOR.random_value(response_schema)

    @staticmethod
    def user_list(request, offset=None, limit=None, birth_date=None, country=None, date_joined=None, email=None, email_verified=None, first_name=None, gender=None, is_active=None, last_login=None, last_name=None, msisdn=None, msisdn_verified=None, nickname=None, organisation_id=None, updated_at=None, username=None, q=None, tfa_enabled=None, has_organisation=None, order_by=None, user_ids=None, site_ids=None, *args, **kwargs):
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
            "organisation_id": {
                "readOnly": true,
                "type": "integer"
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
