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
        :param offset: (optional) An optional query parameter specifying the offset in the result set to start from.
        :type offset: integer
        :param limit: (optional) An optional query parameter to limit the number of results returned.
        :type limit: integer
        :param client_ids: (optional) An optional list of client ids
        :type client_ids: array
        :param client_token_id: (optional) An optional client id to filter on. This is not the primary key.
        :type client_token_id: string
        """
        raise NotImplementedError()

    # client_read -- Synchronisation point for meld
    @staticmethod
    def client_read(request, client_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param client_id: A string value identifying the client
        :type client_id: string
        """
        raise NotImplementedError()

    # country_list -- Synchronisation point for meld
    @staticmethod
    def country_list(request, offset=None, limit=None, country_codes=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param offset: (optional) An optional query parameter specifying the offset in the result set to start from.
        :type offset: integer
        :param limit: (optional) An optional query parameter to limit the number of results returned.
        :type limit: integer
        :param country_codes: (optional) An optional list of country codes
        :type country_codes: array
        """
        raise NotImplementedError()

    # country_read -- Synchronisation point for meld
    @staticmethod
    def country_read(request, country_code, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param country_code: A string value identifying the country
        :type country_code: string
        """
        raise NotImplementedError()

    # invitation_send -- Synchronisation point for meld
    @staticmethod
    def invitation_send(request, invitation_id, language=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param invitation_id: 
        :type invitation_id: string
        :param language: (optional) 
        :type language: string
        """
        raise NotImplementedError()

    # purge_expired_invitations -- Synchronisation point for meld
    @staticmethod
    def purge_expired_invitations(request, cutoff_date=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param cutoff_date: (optional) An optional cutoff date to purge invites before this date
        :type cutoff_date: string
        """
        raise NotImplementedError()

    # organisation_list -- Synchronisation point for meld
    @staticmethod
    def organisation_list(request, offset=None, limit=None, organisation_ids=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param offset: (optional) An optional query parameter specifying the offset in the result set to start from.
        :type offset: integer
        :param limit: (optional) An optional query parameter to limit the number of results returned.
        :type limit: integer
        :param organisation_ids: (optional) An optional list of organisation ids
        :type organisation_ids: array
        """
        raise NotImplementedError()

    # organisation_create -- Synchronisation point for meld
    @staticmethod
    def organisation_create(request, body, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param body: A dictionary containing the parsed and validated body
        :type body: dict
        """
        raise NotImplementedError()

    # organisation_delete -- Synchronisation point for meld
    @staticmethod
    def organisation_delete(request, organisation_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param organisation_id: An integer identifying an organisation a user belongs to
        :type organisation_id: integer
        """
        raise NotImplementedError()

    # organisation_read -- Synchronisation point for meld
    @staticmethod
    def organisation_read(request, organisation_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param organisation_id: An integer identifying an organisation a user belongs to
        :type organisation_id: integer
        """
        raise NotImplementedError()

    # organisation_update -- Synchronisation point for meld
    @staticmethod
    def organisation_update(request, body, organisation_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param body: A dictionary containing the parsed and validated body
        :type body: dict
        :param organisation_id: An integer identifying an organisation a user belongs to
        :type organisation_id: integer
        """
        raise NotImplementedError()

    # user_list -- Synchronisation point for meld
    @staticmethod
    def user_list(request, offset=None, limit=None, birth_date=None, country=None, date_joined=None, email=None, email_verified=None, first_name=None, gender=None, is_active=None, last_login=None, last_name=None, msisdn=None, msisdn_verified=None, nickname=None, organisation_id=None, updated_at=None, username=None, q=None, tfa_enabled=None, has_organisation=None, order_by=None, user_ids=None, site_ids=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param offset: (optional) An optional query parameter specifying the offset in the result set to start from.
        :type offset: integer
        :param limit: (optional) An optional query parameter to limit the number of results returned.
        :type limit: integer
        :param birth_date: (optional) An optional birth_date range filter
        :type birth_date: string
        :param country: (optional) An optional country filter
        :type country: string
        :param date_joined: (optional) An optional date joined range filter
        :type date_joined: string
        :param email: (optional) An optional case insensitive email inner match filter
        :type email: string
        :param email_verified: (optional) An optional email verified filter
        :type email_verified: boolean
        :param first_name: (optional) An optional case insensitive first name inner match filter
        :type first_name: string
        :param gender: (optional) An optional gender filter
        :type gender: string
        :param is_active: (optional) An optional is_active filter
        :type is_active: boolean
        :param last_login: (optional) An optional last login range filter
        :type last_login: string
        :param last_name: (optional) An optional case insensitive last name inner match filter
        :type last_name: string
        :param msisdn: (optional) An optional case insensitive MSISDN inner match filter
        :type msisdn: string
        :param msisdn_verified: (optional) An optional MSISDN verified filter
        :type msisdn_verified: boolean
        :param nickname: (optional) An optional case insensitive nickname inner match filter
        :type nickname: string
        :param organisation_id: (optional) An optional filter on the organisation id
        :type organisation_id: integer
        :param updated_at: (optional) An optional updated_at range filter
        :type updated_at: string
        :param username: (optional) An optional case insensitive username inner match filter
        :type username: string
        :param q: (optional) An optional case insensitive inner match filter across all searchable text fields
        :type q: string
        :param tfa_enabled: (optional) An optional filter based on whether a user has 2FA enabled or not
        :type tfa_enabled: boolean
        :param has_organisation: (optional) An optional filter based on whether a user belongs to an organisation or not
        :type has_organisation: boolean
        :param order_by: (optional) Fields and directions to order by, e.g. "-created_at,username". Add "-" in front of a field name to indicate descending order.
        :type order_by: array
        :param user_ids: (optional) An optional list of user ids
        :type user_ids: array
        :param site_ids: (optional) An optional list of site ids
        :type site_ids: array
        """
        raise NotImplementedError()

    # user_delete -- Synchronisation point for meld
    @staticmethod
    def user_delete(request, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param user_id: A UUID value identifying the user.
        :type user_id: string
        """
        raise NotImplementedError()

    # user_read -- Synchronisation point for meld
    @staticmethod
    def user_read(request, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param user_id: A UUID value identifying the user.
        :type user_id: string
        """
        raise NotImplementedError()

    # user_update -- Synchronisation point for meld
    @staticmethod
    def user_update(request, body, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param body: A dictionary containing the parsed and validated body
        :type body: dict
        :param user_id: A UUID value identifying the user.
        :type user_id: string
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
        :param offset: (optional) An optional query parameter specifying the offset in the result set to start from.
        :type offset: integer
        :param limit: (optional) An optional query parameter to limit the number of results returned.
        :type limit: integer
        :param client_ids: (optional) An optional list of client ids
        :type client_ids: array
        :param client_token_id: (optional) An optional client id to filter on. This is not the primary key.
        :type client_token_id: string
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
        :param client_id: A string value identifying the client
        :type client_id: string
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
        :param offset: (optional) An optional query parameter specifying the offset in the result set to start from.
        :type offset: integer
        :param limit: (optional) An optional query parameter to limit the number of results returned.
        :type limit: integer
        :param country_codes: (optional) An optional list of country codes
        :type country_codes: array
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
        :param country_code: A string value identifying the country
        :type country_code: string
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
        :param invitation_id: 
        :type invitation_id: string
        :param language: (optional) 
        :type language: string
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
        :param cutoff_date: (optional) An optional cutoff date to purge invites before this date
        :type cutoff_date: string
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
        :param offset: (optional) An optional query parameter specifying the offset in the result set to start from.
        :type offset: integer
        :param limit: (optional) An optional query parameter to limit the number of results returned.
        :type limit: integer
        :param organisation_ids: (optional) An optional list of organisation ids
        :type organisation_ids: array
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
    def organisation_create(request, body, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param body: A dictionary containing the parsed and validated body
        :type body: dict
        """
        response_schema = schemas.organisation
        if "type" not in response_schema:
            response_schema["type"] = "object"

        if response_schema["type"] == "array" and "type" not in response_schema["items"]:
            response_schema["items"]["type"] = "object"

        return MockedStubClass.GENERATOR.random_value(response_schema)

    @staticmethod
    def organisation_delete(request, organisation_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param organisation_id: An integer identifying an organisation a user belongs to
        :type organisation_id: integer
        """
        response_schema = schemas.__UNSPECIFIED__
        if "type" not in response_schema:
            response_schema["type"] = "object"

        if response_schema["type"] == "array" and "type" not in response_schema["items"]:
            response_schema["items"]["type"] = "object"

        return MockedStubClass.GENERATOR.random_value(response_schema)

    @staticmethod
    def organisation_read(request, organisation_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param organisation_id: An integer identifying an organisation a user belongs to
        :type organisation_id: integer
        """
        response_schema = schemas.organisation
        if "type" not in response_schema:
            response_schema["type"] = "object"

        if response_schema["type"] == "array" and "type" not in response_schema["items"]:
            response_schema["items"]["type"] = "object"

        return MockedStubClass.GENERATOR.random_value(response_schema)

    @staticmethod
    def organisation_update(request, body, organisation_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param body: A dictionary containing the parsed and validated body
        :type body: dict
        :param organisation_id: An integer identifying an organisation a user belongs to
        :type organisation_id: integer
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
        :param offset: (optional) An optional query parameter specifying the offset in the result set to start from.
        :type offset: integer
        :param limit: (optional) An optional query parameter to limit the number of results returned.
        :type limit: integer
        :param birth_date: (optional) An optional birth_date range filter
        :type birth_date: string
        :param country: (optional) An optional country filter
        :type country: string
        :param date_joined: (optional) An optional date joined range filter
        :type date_joined: string
        :param email: (optional) An optional case insensitive email inner match filter
        :type email: string
        :param email_verified: (optional) An optional email verified filter
        :type email_verified: boolean
        :param first_name: (optional) An optional case insensitive first name inner match filter
        :type first_name: string
        :param gender: (optional) An optional gender filter
        :type gender: string
        :param is_active: (optional) An optional is_active filter
        :type is_active: boolean
        :param last_login: (optional) An optional last login range filter
        :type last_login: string
        :param last_name: (optional) An optional case insensitive last name inner match filter
        :type last_name: string
        :param msisdn: (optional) An optional case insensitive MSISDN inner match filter
        :type msisdn: string
        :param msisdn_verified: (optional) An optional MSISDN verified filter
        :type msisdn_verified: boolean
        :param nickname: (optional) An optional case insensitive nickname inner match filter
        :type nickname: string
        :param organisation_id: (optional) An optional filter on the organisation id
        :type organisation_id: integer
        :param updated_at: (optional) An optional updated_at range filter
        :type updated_at: string
        :param username: (optional) An optional case insensitive username inner match filter
        :type username: string
        :param q: (optional) An optional case insensitive inner match filter across all searchable text fields
        :type q: string
        :param tfa_enabled: (optional) An optional filter based on whether a user has 2FA enabled or not
        :type tfa_enabled: boolean
        :param has_organisation: (optional) An optional filter based on whether a user belongs to an organisation or not
        :type has_organisation: boolean
        :param order_by: (optional) Fields and directions to order by, e.g. "-created_at,username". Add "-" in front of a field name to indicate descending order.
        :type order_by: array
        :param user_ids: (optional) An optional list of user ids
        :type user_ids: array
        :param site_ids: (optional) An optional list of site ids
        :type site_ids: array
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
        :param user_id: A UUID value identifying the user.
        :type user_id: string
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
        :param user_id: A UUID value identifying the user.
        :type user_id: string
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
        :param body: A dictionary containing the parsed and validated body
        :type body: dict
        :param user_id: A UUID value identifying the user.
        :type user_id: string
        """
        response_schema = schemas.user
        if "type" not in response_schema:
            response_schema["type"] = "object"

        if response_schema["type"] == "array" and "type" not in response_schema["items"]:
            response_schema["items"]["type"] = "object"

        return MockedStubClass.GENERATOR.random_value(response_schema)
