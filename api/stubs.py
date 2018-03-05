"""
Do not modify this file. It is generated from the Swagger specification.
"""
import json
from apitools.datagenerator import DataGenerator

import authentication-service.api.schemas as schemas


class AbstractStubClass(object):
    """
    Implementations need to be derived from this class.
    """

    @staticmethod
    def client_list(request, limit=None, offset=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        """
        raise NotImplementedError()

    @staticmethod
    def client_read(request, client_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param client_id: string A UUID value identifying the client
        """
        raise NotImplementedError()

    @staticmethod
    def authorize(request, state, redirect_uri, response_type, client_id, scope, nonce=None, max_age=None, prompt=None, ui_locales=None, response_mode=None, display=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param state: string An opaque string that will be passed back to the redirect URL and therefore can be used to communicate client side state and prevent CSRF attacks.

        :param redirect_uri: string The location to redirect to after (un)successful authentication. See OIDC for the parameters passed in the query string (`response_mode=query`) or as fragments (`response_mode=fragment`). This must be one of the registered redirect URLs.

        :param response_type: string The OIDC response type to use for this authentication flow. Valid choices are `code`, `id_token`, `token`, `token id_token`, `code id_token` `code token` and `code token id_token`, but a client can be configured with a more restricted set.

        :param client_id: string A client ID obtained from the [Dashboard](https://localhost:8000/admin/).

        :param scope: string The space-separated identity claims to request from the end-user. Always include `openid` as a scope for compatibility with OIDC.

        """
        raise NotImplementedError()

    @staticmethod
    def token(request, body, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param body: dict A dictionary containing the parsed and validated body
        """
        raise NotImplementedError()

    @staticmethod
    def userInfo(request, *args, **kwargs):
        """
        :param request: An HttpRequest
        """
        raise NotImplementedError()

    @staticmethod
    def user_list(request, limit=None, email=None, offset=None, *args, **kwargs):
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
    def client_list(request, limit=None, offset=None, *args, **kwargs):
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
            "client_type": {
                "description": "<b>Confidential</b> clients are capable of maintaining the confidentiality of their credentials. <b>Public</b> clients are incapable.", 
                "type": "string"
            }, 
            "contact_email": {
                "description": "", 
                "type": "string"
            }, 
            "jwt_alg": {
                "description": "Algorithm used to encode ID Tokens.", 
                "type": "string"
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
        :param client_id: string A UUID value identifying the client
        """
        response_schema = schemas.client
        if "type" not in response_schema:
            response_schema["type"] = "object"

        if response_schema["type"] == "array" and "type" not in response_schema["items"]:
            response_schema["items"]["type"] = "object"

        return MockedStubClass.GENERATOR.random_value(response_schema)

    @staticmethod
    def authorize(request, state, redirect_uri, response_type, client_id, scope, nonce=None, max_age=None, prompt=None, ui_locales=None, response_mode=None, display=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param state: string An opaque string that will be passed back to the redirect URL and therefore can be used to communicate client side state and prevent CSRF attacks.

        :param redirect_uri: string The location to redirect to after (un)successful authentication. See OIDC for the parameters passed in the query string (`response_mode=query`) or as fragments (`response_mode=fragment`). This must be one of the registered redirect URLs.

        :param response_type: string The OIDC response type to use for this authentication flow. Valid choices are `code`, `id_token`, `token`, `token id_token`, `code id_token` `code token` and `code token id_token`, but a client can be configured with a more restricted set.

        :param client_id: string A client ID obtained from the [Dashboard](https://localhost:8000/admin/).

        :param scope: string The space-separated identity claims to request from the end-user. Always include `openid` as a scope for compatibility with OIDC.

        """
        response_schema = schemas.__UNSPECIFIED__
        if "type" not in response_schema:
            response_schema["type"] = "object"

        if response_schema["type"] == "array" and "type" not in response_schema["items"]:
            response_schema["items"]["type"] = "object"

        return MockedStubClass.GENERATOR.random_value(response_schema)

    @staticmethod
    def token(request, body, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param body: dict A dictionary containing the parsed and validated body
        """
        response_schema = schemas.__UNSPECIFIED__
        if "type" not in response_schema:
            response_schema["type"] = "object"

        if response_schema["type"] == "array" and "type" not in response_schema["items"]:
            response_schema["items"]["type"] = "object"

        return MockedStubClass.GENERATOR.random_value(response_schema)

    @staticmethod
    def userInfo(request, *args, **kwargs):
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
    def user_list(request, limit=None, email=None, offset=None, *args, **kwargs):
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
            "date_joined"
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
        response_schema = schemas.__UNSPECIFIED__
        if "type" not in response_schema:
            response_schema["type"] = "object"

        if response_schema["type"] == "array" and "type" not in response_schema["items"]:
            response_schema["items"]["type"] = "object"

        return MockedStubClass.GENERATOR.random_value(response_schema)
