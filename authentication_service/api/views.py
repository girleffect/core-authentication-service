"""
Do not modify this file. It is generated from the Swagger specification.

"""
import importlib
import logging
import json
import jsonschema
from jsonschema import ValidationError

from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View

import authentication_service.api.schemas as schemas
import authentication_service.api.utils as utils

# Set up logging
logging.basicConfig(level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

try:
    VALIDATE_RESPONSES = settings.SWAGGER_API_VALIDATE_RESPONSES
except AttributeError:
    VALIDATE_RESPONSES = False
LOGGER.info("Swagger API response validation is {}".format(
    "on" if VALIDATE_RESPONSES else "off"
))

# Set up the stub class. If it is not explicitly configured in the settings.py
# file of the project, we default to a mocked class.
try:
    stub_class_path = settings.STUBS_CLASS
except AttributeError:
    stub_class_path = "authentication_service.api.stubs.MockedStubClass"

module_name, class_name = stub_class_path.rsplit(".", 1)
Module = importlib.import_module(module_name)
Stubs = getattr(Module, class_name)


def maybe_validate_result(result, schema):
    if VALIDATE_RESPONSES:
        try:
            jsonschema.validate(result, schema)
        except ValidationError as e:
            LOGGER.error(e.message)


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(utils.login_required_no_redirect, name="get")
class Clients(View):

    GET_RESPONSE_SCHEMA = json.loads("""{
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

    def get(self, request, *args, **kwargs):
        """
        :param self: A Clients instance
        :param request: An HttpRequest
        """
        # offset (optional): integer An optional query parameter specifying the offset in the result set to start from.
        offset = request.GET.get("offset", None)
        # limit (optional): integer An optional query parameter to limit the number of results returned.
        limit = request.GET.get("limit", None)
        # client_ids (optional): array An optional list of client ids
        client_ids = request.GET.getlist("client_ids", None)
        # client_token_id (optional): string An optional client id to filter on. This is not the primary key.
        client_token_id = request.GET.get("client_token_id", None)
        result = Stubs.client_list(request, offset, limit, client_ids, client_token_id, )

        if type(result) is tuple:
            result, headers = result
        else:
            headers = {}
        maybe_validate_result(result, self.GET_RESPONSE_SCHEMA)

        response = JsonResponse(result, safe=False)
        for key, val in headers.items():
            response[key] = val
        return response


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(utils.login_required_no_redirect, name="get")
class ClientsClientId(View):

    GET_RESPONSE_SCHEMA = schemas.client

    def get(self, request, client_id, *args, **kwargs):
        """
        :param self: A ClientsClientId instance
        :param request: An HttpRequest
        :param client_id: string A string value identifying the client
        """
        result = Stubs.client_read(request, client_id, )

        if type(result) is tuple:
            result, headers = result
        else:
            headers = {}
        maybe_validate_result(result, self.GET_RESPONSE_SCHEMA)

        response = JsonResponse(result, safe=False)
        for key, val in headers.items():
            response[key] = val
        return response


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(utils.login_required_no_redirect, name="get")
class Users(View):

    GET_RESPONSE_SCHEMA = json.loads("""{
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

    def get(self, request, *args, **kwargs):
        """
        :param self: A Users instance
        :param request: An HttpRequest
        """
        # offset (optional): integer An optional query parameter specifying the offset in the result set to start from.
        offset = request.GET.get("offset", None)
        # limit (optional): integer An optional query parameter to limit the number of results returned.
        limit = request.GET.get("limit", None)
        # birth_date (optional): string An optional birth_date range filter
        birth_date = request.GET.get("birth_date", None)
        # country (optional): string An optional country filter
        country = request.GET.get("country", None)
        # date_joined (optional): string An optional date joined range filter
        date_joined = request.GET.get("date_joined", None)
        # email (optional): string An optional case insensitive email inner match filter
        email = request.GET.get("email", None)
        # email_verified (optional): boolean An optional email verified filter
        email_verified = request.GET.get("email_verified", None)
        # first_name (optional): string An optional case insensitive first name inner match filter
        first_name = request.GET.get("first_name", None)
        # gender (optional): string An optional gender filter
        gender = request.GET.get("gender", None)
        # is_active (optional): boolean An optional is_active filter
        is_active = request.GET.get("is_active", None)
        # last_login (optional): string An optional last login range filter
        last_login = request.GET.get("last_login", None)
        # last_name (optional): string An optional case insensitive last name inner match filter
        last_name = request.GET.get("last_name", None)
        # msisdn (optional): string An optional case insensitive MSISDN inner match filter
        msisdn = request.GET.get("msisdn", None)
        # msisdn_verified (optional): boolean An optional MSISDN verified filter
        msisdn_verified = request.GET.get("msisdn_verified", None)
        # nickname (optional): string An optional case insensitive nickname inner match filter
        nickname = request.GET.get("nickname", None)
        # organisational_unit_id (optional): integer An optional filter on the organisational unit id
        organisational_unit_id = request.GET.get("organisational_unit_id", None)
        # updated_at (optional): string An optional updated_at range filter
        updated_at = request.GET.get("updated_at", None)
        # username (optional): string An optional case insensitive username inner match filter
        username = request.GET.get("username", None)
        # q (optional): string An optional case insensitive inner match filter across all searchable text fields
        q = request.GET.get("q", None)
        # tfa_enabled (optional): boolean An optional filter based on whether a user has 2FA enabled or not
        tfa_enabled = request.GET.get("tfa_enabled", None)
        # has_organisational_unit (optional): boolean An optional filter based on whether a user has an organisational unit or not
        has_organisational_unit = request.GET.get("has_organisational_unit", None)
        # order_by (optional): array Fields and directions to order by, e.g. "-created_at,username". Add "-" in front of a field name to indicate descending order.
        order_by = request.GET.get("order_by", None)
        if order_by is not None:
            order_by = order_by.split(",")
        # user_ids (optional): array An optional list of user ids
        user_ids = request.GET.getlist("user_ids", None)
        result = Stubs.user_list(request, offset, limit, birth_date, country, date_joined, email, email_verified, first_name, gender, is_active, last_login, last_name, msisdn, msisdn_verified, nickname, organisational_unit_id, updated_at, username, q, tfa_enabled, has_organisational_unit, order_by, user_ids, )

        if type(result) is tuple:
            result, headers = result
        else:
            headers = {}
        maybe_validate_result(result, self.GET_RESPONSE_SCHEMA)

        response = JsonResponse(result, safe=False)
        for key, val in headers.items():
            response[key] = val
        return response


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(utils.login_required_no_redirect, name="delete")
@method_decorator(utils.login_required_no_redirect, name="get")
@method_decorator(utils.login_required_no_redirect, name="put")
class UsersUserId(View):

    DELETE_RESPONSE_SCHEMA = schemas.__UNSPECIFIED__
    GET_RESPONSE_SCHEMA = schemas.user
    PUT_RESPONSE_SCHEMA = schemas.user
    PUT_BODY_SCHEMA = schemas.user_update

    def delete(self, request, user_id, *args, **kwargs):
        """
        :param self: A UsersUserId instance
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        result = Stubs.user_delete(request, user_id, )

        if type(result) is tuple:
            result, headers = result
        else:
            headers = {}
        maybe_validate_result(result, self.DELETE_RESPONSE_SCHEMA)

        response = JsonResponse(result, safe=False)
        for key, val in headers.items():
            response[key] = val
        return response

    def get(self, request, user_id, *args, **kwargs):
        """
        :param self: A UsersUserId instance
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        result = Stubs.user_read(request, user_id, )

        if type(result) is tuple:
            result, headers = result
        else:
            headers = {}
        maybe_validate_result(result, self.GET_RESPONSE_SCHEMA)

        response = JsonResponse(result, safe=False)
        for key, val in headers.items():
            response[key] = val
        return response

    def put(self, request, user_id, *args, **kwargs):
        """
        :param self: A UsersUserId instance
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        body = utils.body_to_dict(request.body, self.PUT_BODY_SCHEMA)
        if not body:
            return HttpResponseBadRequest("Body required")

        result = Stubs.user_update(request, body, user_id, )

        if type(result) is tuple:
            result, headers = result
        else:
            headers = {}
        maybe_validate_result(result, self.PUT_RESPONSE_SCHEMA)

        response = JsonResponse(result, safe=False)
        for key, val in headers.items():
            response[key] = val
        return response


class __SWAGGER_SPEC__(View):

    def get(self, request, *args, **kwargs):
        spec = json.loads("""{
    "basePath": "/api/v1",
    "definitions": {
        "client": {
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
            "type": "object"
        },
        "user": {
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
            "type": "object"
        },
        "user_update": {
            "minProperties": 1,
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
                "is_active": {
                    "description": "Designates whether this user should be treated as active. Deselect this instead of deleting accounts.",
                    "type": "boolean"
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
                }
            },
            "type": "object"
        }
    },
    "externalDocs": {
        "description": "Girl Effect Developer Docs",
        "url": "https://girleffect.github.io/core-access-control/"
    },
    "host": "localhost:8000",
    "info": {
        "description": "This is the API that will be exposed by the Authentication Service.\\nThe Authentication Service facilitates user registration and login via web-based flows as defined for the OpenID Connect specification.\\n",
        "title": "Authentication Service API",
        "version": "1.0"
    },
    "parameters": {
        "client_id": {
            "description": "A string value identifying the client",
            "format": "string",
            "in": "path",
            "name": "client_id",
            "required": true,
            "type": "string"
        },
        "optional_limit": {
            "default": 20,
            "description": "An optional query parameter to limit the number of results returned.",
            "in": "query",
            "maximum": 100,
            "minimum": 1,
            "name": "limit",
            "required": false,
            "type": "integer"
        },
        "optional_offset": {
            "default": 0,
            "description": "An optional query parameter specifying the offset in the result set to start from.",
            "in": "query",
            "minimum": 0,
            "name": "offset",
            "required": false,
            "type": "integer"
        },
        "user_id": {
            "description": "A UUID value identifying the user.",
            "format": "uuid",
            "in": "path",
            "name": "user_id",
            "required": true,
            "type": "string"
        }
    },
    "paths": {
        "/clients": {
            "get": {
                "operationId": "client_list",
                "parameters": [
                    {
                        "$ref": "#/parameters/optional_offset",
                        "x-scope": [
                            ""
                        ]
                    },
                    {
                        "$ref": "#/parameters/optional_limit",
                        "x-scope": [
                            ""
                        ]
                    },
                    {
                        "collectionFormat": "multi",
                        "description": "An optional list of client ids",
                        "in": "query",
                        "items": {
                            "type": "integer"
                        },
                        "minItems": 0,
                        "name": "client_ids",
                        "required": false,
                        "type": "array",
                        "uniqueItems": true
                    },
                    {
                        "description": "An optional client id to filter on. This is not the primary key.",
                        "in": "query",
                        "name": "client_token_id",
                        "required": false,
                        "type": "string"
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "",
                        "schema": {
                            "items": {
                                "$ref": "#/definitions/client",
                                "x-scope": [
                                    ""
                                ]
                            },
                            "type": "array"
                        }
                    }
                },
                "tags": [
                    "authentication"
                ]
            }
        },
        "/clients/{client_id}": {
            "get": {
                "operationId": "client_read",
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "",
                        "schema": {
                            "$ref": "#/definitions/client",
                            "x-scope": [
                                ""
                            ]
                        }
                    }
                },
                "tags": [
                    "authentication"
                ]
            },
            "parameters": [
                {
                    "$ref": "#/parameters/client_id",
                    "x-scope": [
                        ""
                    ]
                }
            ]
        },
        "/users": {
            "get": {
                "operationId": "user_list",
                "parameters": [
                    {
                        "$ref": "#/parameters/optional_offset",
                        "x-scope": [
                            ""
                        ]
                    },
                    {
                        "$ref": "#/parameters/optional_limit",
                        "x-scope": [
                            ""
                        ]
                    },
                    {
                        "description": "An optional birth_date range filter",
                        "in": "query",
                        "name": "birth_date",
                        "required": false,
                        "type": "string"
                    },
                    {
                        "description": "An optional country filter",
                        "in": "query",
                        "maxLength": 2,
                        "minLength": 2,
                        "name": "country",
                        "required": false,
                        "type": "string"
                    },
                    {
                        "description": "An optional date joined range filter",
                        "in": "query",
                        "name": "date_joined",
                        "required": false,
                        "type": "string"
                    },
                    {
                        "description": "An optional case insensitive email inner match filter",
                        "in": "query",
                        "minLength": 3,
                        "name": "email",
                        "required": false,
                        "type": "string"
                    },
                    {
                        "description": "An optional email verified filter",
                        "in": "query",
                        "name": "email_verified",
                        "required": false,
                        "type": "boolean"
                    },
                    {
                        "description": "An optional case insensitive first name inner match filter",
                        "in": "query",
                        "minLength": 3,
                        "name": "first_name",
                        "required": false,
                        "type": "string"
                    },
                    {
                        "description": "An optional gender filter",
                        "in": "query",
                        "name": "gender",
                        "required": false,
                        "type": "string"
                    },
                    {
                        "description": "An optional is_active filter",
                        "in": "query",
                        "name": "is_active",
                        "required": false,
                        "type": "boolean"
                    },
                    {
                        "description": "An optional last login range filter",
                        "in": "query",
                        "name": "last_login",
                        "required": false,
                        "type": "string"
                    },
                    {
                        "description": "An optional case insensitive last name inner match filter",
                        "in": "query",
                        "minLength": 3,
                        "name": "last_name",
                        "required": false,
                        "type": "string"
                    },
                    {
                        "description": "An optional case insensitive MSISDN inner match filter",
                        "in": "query",
                        "minLength": 3,
                        "name": "msisdn",
                        "required": false,
                        "type": "string"
                    },
                    {
                        "description": "An optional MSISDN verified filter",
                        "in": "query",
                        "name": "msisdn_verified",
                        "required": false,
                        "type": "boolean"
                    },
                    {
                        "description": "An optional case insensitive nickname inner match filter",
                        "in": "query",
                        "minLength": 3,
                        "name": "nickname",
                        "required": false,
                        "type": "string"
                    },
                    {
                        "description": "An optional filter on the organisational unit id",
                        "in": "query",
                        "name": "organisational_unit_id",
                        "required": false,
                        "type": "integer"
                    },
                    {
                        "description": "An optional updated_at range filter",
                        "in": "query",
                        "name": "updated_at",
                        "required": false,
                        "type": "string"
                    },
                    {
                        "description": "An optional case insensitive username inner match filter",
                        "in": "query",
                        "minLength": 3,
                        "name": "username",
                        "required": false,
                        "type": "string"
                    },
                    {
                        "description": "An optional case insensitive inner match filter across all searchable text fields",
                        "in": "query",
                        "minLength": 3,
                        "name": "q",
                        "required": false,
                        "type": "string"
                    },
                    {
                        "description": "An optional filter based on whether a user has 2FA enabled or not",
                        "in": "query",
                        "name": "tfa_enabled",
                        "required": false,
                        "type": "boolean"
                    },
                    {
                        "description": "An optional filter based on whether a user has an organisational unit or not",
                        "in": "query",
                        "name": "has_organisational_unit",
                        "required": false,
                        "type": "boolean"
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "Fields and directions to order by, e.g. \\"-created_at,username\\". Add \\"-\\" in front of a field name to indicate descending order.",
                        "in": "query",
                        "items": {
                            "type": "string"
                        },
                        "name": "order_by",
                        "required": false,
                        "type": "array",
                        "uniqueItems": true
                    },
                    {
                        "collectionFormat": "multi",
                        "description": "An optional list of user ids",
                        "in": "query",
                        "items": {
                            "format": "uuid",
                            "type": "string"
                        },
                        "minItems": 0,
                        "name": "user_ids",
                        "required": false,
                        "type": "array",
                        "uniqueItems": true
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "",
                        "schema": {
                            "items": {
                                "$ref": "#/definitions/user",
                                "x-scope": [
                                    ""
                                ]
                            },
                            "type": "array"
                        }
                    }
                },
                "tags": [
                    "authentication"
                ]
            }
        },
        "/users/{user_id}": {
            "delete": {
                "operationId": "user_delete",
                "responses": {
                    "204": {
                        "description": ""
                    }
                },
                "tags": [
                    "authentication"
                ]
            },
            "get": {
                "operationId": "user_read",
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "",
                        "schema": {
                            "$ref": "#/definitions/user",
                            "x-scope": [
                                ""
                            ]
                        }
                    }
                },
                "tags": [
                    "authentication"
                ]
            },
            "parameters": [
                {
                    "$ref": "#/parameters/user_id",
                    "x-scope": [
                        ""
                    ]
                }
            ],
            "put": {
                "consumes": [
                    "application/json"
                ],
                "operationId": "user_update",
                "parameters": [
                    {
                        "in": "body",
                        "name": "data",
                        "schema": {
                            "$ref": "#/definitions/user_update",
                            "x-scope": [
                                ""
                            ]
                        }
                    }
                ],
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "",
                        "schema": {
                            "$ref": "#/definitions/user",
                            "x-scope": [
                                ""
                            ]
                        }
                    }
                },
                "tags": [
                    "authentication"
                ]
            }
        }
    },
    "schemes": [
        "https",
        "http"
    ],
    "security": [
        {
            "APIKeyHeader": []
        }
    ],
    "securityDefinitions": {
        "APIKeyHeader": {
            "in": "header",
            "name": "X-API-Key",
            "type": "apiKey"
        }
    },
    "swagger": "2.0"
}""")
        # Mod spec to point to demo application
        spec["basePath"] = "/"
        spec["host"] = "localhost:8000"
        # Add basic auth as a security definition
        security_definitions = spec.get("securityDefinitions", {})
        security_definitions["basic_auth"] = {"type": "basic"}
        spec["securityDefinitions"] = security_definitions
        return JsonResponse(spec)
