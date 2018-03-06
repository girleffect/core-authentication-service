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
        maybe_validate_result(result, self.GET_RESPONSE_SCHEMA)

        return JsonResponse(result, safe=False)


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
        maybe_validate_result(result, self.GET_RESPONSE_SCHEMA)

        return JsonResponse(result, safe=False)


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

    def get(self, request, *args, **kwargs):
        """
        :param self: A Users instance
        :param request: An HttpRequest
        """
        # offset (optional): integer An optional query parameter specifying the offset in the result set to start from.
        offset = request.GET.get("offset", None)
        # limit (optional): integer An optional query parameter to limit the number of results returned.
        limit = request.GET.get("limit", None)
        # email (optional): string An optional email filter
        email = request.GET.get("email", None)
        # username_prefix (optional): string An optional username prefix filter
        username_prefix = request.GET.get("username_prefix", None)
        # user_ids (optional): array An optional list of user ids
        user_ids = request.GET.getlist("user_ids", None)
        result = Stubs.user_list(request, offset, limit, email, username_prefix, user_ids, )
        maybe_validate_result(result, self.GET_RESPONSE_SCHEMA)

        return JsonResponse(result, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(utils.login_required_no_redirect, name="delete")
@method_decorator(utils.login_required_no_redirect, name="get")
@method_decorator(utils.login_required_no_redirect, name="put")
class UsersUserId(View):

    DELETE_RESPONSE_SCHEMA = schemas.__UNSPECIFIED__
    GET_RESPONSE_SCHEMA = schemas.user
    PUT_RESPONSE_SCHEMA = schemas.__UNSPECIFIED__
    PUT_BODY_SCHEMA = schemas.user_update

    def delete(self, request, user_id, *args, **kwargs):
        """
        :param self: A UsersUserId instance
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        result = Stubs.user_delete(request, user_id, )
        maybe_validate_result(result, self.DELETE_RESPONSE_SCHEMA)

        return JsonResponse(result, safe=False)

    def get(self, request, user_id, *args, **kwargs):
        """
        :param self: A UsersUserId instance
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        result = Stubs.user_read(request, user_id, )
        maybe_validate_result(result, self.GET_RESPONSE_SCHEMA)

        return JsonResponse(result, safe=False)

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
        maybe_validate_result(result, self.PUT_RESPONSE_SCHEMA)

        return JsonResponse(result, safe=False)


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
                        "description": "An optional email filter",
                        "format": "email",
                        "in": "query",
                        "name": "email",
                        "required": false,
                        "type": "string"
                    },
                    {
                        "description": "An optional username prefix filter",
                        "in": "query",
                        "name": "username_prefix",
                        "required": false,
                        "type": "string"
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
                        "description": ""
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
