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

import authentication-service.api.schemas as schemas
import authentication-service.api.utils as utils

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
    stub_class_path = "authentication-service.api.stubs.MockedStubClass"

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
                "description": "If enabled, the Server will save the user consent given to a specific client, so that user wont be prompted for the same authorization multiple times.", 
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
        limit = request.GET.get("limit", None)
        offset = request.GET.get("offset", None)
        result = Stubs.client_list(request, limit, offset, )
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
        :param client_id: string A UUID value identifying the client
        """
        result = Stubs.client_read(request, client_id, )
        maybe_validate_result(result, self.GET_RESPONSE_SCHEMA)

        return JsonResponse(result, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(utils.login_required_no_redirect, name="get")
class OpenidAuthorize(View):

    GET_RESPONSE_SCHEMA = schemas.__UNSPECIFIED__

    def get(self, request, *args, **kwargs):
        """
        :param self: A OpenidAuthorize instance
        :param request: An HttpRequest
        """
        try:
            state = request.GET["state"]
        except KeyError:
            return HttpResponseBadRequest("state required")

        try:
            redirect_uri = request.GET["redirect_uri"]
        except KeyError:
            return HttpResponseBadRequest("redirect_uri required")

        try:
            response_type = request.GET["response_type"]
        except KeyError:
            return HttpResponseBadRequest("response_type required")

        try:
            client_id = request.GET["client_id"]
        except KeyError:
            return HttpResponseBadRequest("client_id required")

        try:
            scope = request.GET["scope"]
        except KeyError:
            return HttpResponseBadRequest("scope required")

        nonce = request.GET.get("nonce", None)
        max_age = request.GET.get("max_age", None)
        prompt = request.GET.get("prompt", None)
        ui_locales = request.GET.get("ui_locales", None)
        response_mode = request.GET.get("response_mode", None)
        display = request.GET.get("display", None)
        result = Stubs.authorize(request, state, redirect_uri, response_type, client_id, scope, nonce, max_age, prompt, ui_locales, response_mode, display, )
        maybe_validate_result(result, self.GET_RESPONSE_SCHEMA)

        return JsonResponse(result, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(utils.login_required_no_redirect, name="post")
class OpenidToken(View):

    POST_RESPONSE_SCHEMA = schemas.__UNSPECIFIED__
    POST_BODY_SCHEMA = json.loads("""{
    "properties": {
        "client_id": {
            "description": "The registered client ID.\n", 
            "type": "string"
        }, 
        "client_secret": {
            "description": "The registered client ID secret.\n", 
            "format": "password", 
            "type": "string"
        }, 
        "code": {
            "description": "The authorization code previously obtained from the Authentication endpoint.\n", 
            "type": "string"
        }, 
        "grant_type": {
            "description": "The authorization grant type, must be `authorization_code`.\n", 
            "type": "string"
        }, 
        "redirect_uri": {
            "description": "The redirect URL that was used previously with the Authentication endpoint.\n", 
            "type": "string"
        }
    }, 
    "required": [
        "client_id"
    ], 
    "type": "object"
}""")

    def post(self, request, *args, **kwargs):
        """
        :param self: A OpenidToken instance
        :param request: An HttpRequest
        """
        body = utils.body_to_dict(request.body, self.POST_BODY_SCHEMA)
        if not body:
            return HttpResponseBadRequest("Body required")

        result = Stubs.token(request, body, )
        maybe_validate_result(result, self.POST_RESPONSE_SCHEMA)

        return JsonResponse(result, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(utils.login_required_no_redirect, name="get")
class OpenidUserinfo(View):

    GET_RESPONSE_SCHEMA = schemas.__UNSPECIFIED__

    def get(self, request, *args, **kwargs):
        """
        :param self: A OpenidUserinfo instance
        :param request: An HttpRequest
        """
        result = Stubs.userInfo(request, )
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
        limit = request.GET.get("limit", None)
        email = request.GET.get("email", None)
        offset = request.GET.get("offset", None)
        result = Stubs.user_list(request, limit, email, offset, )
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
        "Address": {
            "description": "OIDC Address structure", 
            "properties": {
                "country": {
                    "type": "string"
                }, 
                "locality": {
                    "type": "string"
                }, 
                "postal_code": {
                    "type": "string"
                }, 
                "region": {
                    "type": "string"
                }, 
                "street_address": {
                    "type": "string"
                }
            }
        }, 
        "Client": {
            "description": "Client object", 
            "properties": {
                "application_type": {
                    "type": "string"
                }, 
                "client_id": {
                    "type": "string"
                }, 
                "client_name": {
                    "type": "string"
                }, 
                "client_uri": {
                    "type": "string"
                }, 
                "contacts": {
                    "items": {
                        "type": "string"
                    }, 
                    "type": "array"
                }, 
                "default_max_age": {
                    "format": "int64", 
                    "type": "integer"
                }, 
                "default_scopes": {
                    "items": {
                        "type": "string"
                    }, 
                    "type": "array"
                }, 
                "grant_types": {
                    "items": {
                        "type": "string"
                    }, 
                    "type": "array"
                }, 
                "logo_uri": {
                    "type": "string"
                }, 
                "policy_uri": {
                    "type": "string"
                }, 
                "redirect_uris": {
                    "items": {
                        "type": "string"
                    }, 
                    "type": "array"
                }, 
                "response_types": {
                    "items": {
                        "type": "string"
                    }, 
                    "type": "array"
                }, 
                "tos_uri": {
                    "type": "string"
                }
            }, 
            "required": [
                "client_name", 
                "client_uri"
            ]
        }, 
        "OAuth2Error": {
            "description": "Error Response defined as in Section 5.2 of OAuth 2.0 [RFC6749].\\n", 
            "properties": {
                "error": {
                    "type": "string"
                }, 
                "error_description": {
                    "type": "string"
                }
            }, 
            "required": [
                "error"
            ]
        }, 
        "ProblemDetail": {
            "description": "HTTP Problem Detail\\n", 
            "properties": {
                "detail": {
                    "description": "Human-readable explanation specific to this occurrence of the problem.\\n", 
                    "type": "string"
                }, 
                "status": {
                    "description": "The HTTP status code for this occurrence of the problem.\\n", 
                    "type": "integer"
                }, 
                "title": {
                    "description": "Human-readable summary of the problem type.\\n", 
                    "type": "string"
                }, 
                "type": {
                    "default": "about:blank", 
                    "type": "string"
                }
            }, 
            "required": [
                "type", 
                "status"
            ]
        }, 
        "Session": {
            "description": "Session object", 
            "properties": {
                "authenticated_at": {
                    "format": "date-time", 
                    "type": "string"
                }, 
                "client_id": {
                    "type": "string"
                }, 
                "client_name": {
                    "type": "string"
                }, 
                "client_uri": {
                    "type": "string"
                }, 
                "concluded_at": {
                    "format": "date-time", 
                    "type": "string"
                }, 
                "connected_at": {
                    "format": "date-time", 
                    "type": "string"
                }, 
                "contacts": {
                    "items": {
                        "type": "string"
                    }, 
                    "type": "array"
                }, 
                "created_at": {
                    "type": "string"
                }, 
                "deleted_at": {
                    "format": "date-time", 
                    "type": "string"
                }, 
                "logo_uri": {
                    "type": "string"
                }, 
                "nonce": {
                    "type": "string"
                }, 
                "policy_uri": {
                    "type": "string"
                }, 
                "redirect_uri": {
                    "type": "string"
                }, 
                "response_mode": {
                    "type": "string"
                }, 
                "response_type": {
                    "type": "string"
                }, 
                "scopes": {
                    "items": {
                        "type": "string"
                    }, 
                    "type": "array"
                }, 
                "scopes_optional": {
                    "items": {
                        "type": "string"
                    }, 
                    "type": "array"
                }, 
                "scopes_required": {
                    "items": {
                        "type": "string"
                    }, 
                    "type": "array"
                }, 
                "scopes_seen": {
                    "items": {
                        "type": "string"
                    }, 
                    "type": "array"
                }, 
                "scopes_signed": {
                    "items": {
                        "type": "string"
                    }, 
                    "type": "array"
                }, 
                "session_id": {
                    "type": "string"
                }, 
                "session_state": {
                    "type": "string"
                }, 
                "session_uri": {
                    "type": "string"
                }, 
                "sub": {
                    "type": "string"
                }, 
                "tokens_seen": {
                    "items": {
                        "type": "string"
                    }, 
                    "type": "array"
                }, 
                "tos_uri": {
                    "type": "string"
                }, 
                "version": {
                    "type": "integer"
                }
            }
        }, 
        "Token": {
            "description": "Successful token response\\n", 
            "properties": {
                "access_token": {
                    "description": "The access token issued by the authorization server.", 
                    "type": "string"
                }, 
                "expires_at": {
                    "description": "The time the access token will expire in seconds since epoch.", 
                    "format": "int64", 
                    "type": "integer"
                }, 
                "expires_in": {
                    "description": "The lifetime in seconds of the access token.", 
                    "format": "int32", 
                    "type": "integer"
                }, 
                "id_token": {
                    "description": "ID Token value associated with the authenticated session.", 
                    "type": "string"
                }, 
                "refresh_token": {
                    "description": "The refresh token issued to the client, if any.", 
                    "type": "string"
                }, 
                "scope": {
                    "description": "The scope of the granted tokens.", 
                    "type": "string"
                }, 
                "token_type": {
                    "type": "string"
                }
            }, 
            "required": [
                "token_type"
            ]
        }, 
        "UserInfo": {
            "description": "OIDC UserInfo structure", 
            "properties": {
                "address": {
                    "$ref": "#/definitions/Address", 
                    "x-scope": [
                        "", 
                        "#/responses/UserInfo", 
                        "#/definitions/UserInfo"
                    ]
                }, 
                "email": {
                    "type": "string"
                }, 
                "email_verified": {
                    "type": "boolean"
                }, 
                "family_name": {
                    "type": "string"
                }, 
                "given_name": {
                    "type": "string"
                }, 
                "name": {
                    "type": "string"
                }, 
                "phone_number": {
                    "type": "string"
                }, 
                "phone_number_verified": {
                    "type": "boolean"
                }, 
                "sub": {
                    "type": "string"
                }
            }, 
            "required": [
                "sub"
            ]
        }, 
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
                    "description": "If enabled, the Server will save the user consent given to a specific client, so that user wont be prompted for the same authorization multiple times.", 
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
        "description": "This is the API that will be exposed by the Authentication Service.\\n\\nThe Authentication Service facilitates user registration and login via web-based flows as defined for the OpenID Connect specification.\\n", 
        "title": "Authentication Service API", 
        "version": "1.0"
    }, 
    "parameters": {
        "client_id": {
            "description": "A UUID value identifying the client", 
            "format": "uuid", 
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
        "/clients/": {
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
                    "oidc_provider"
                ]
            }
        }, 
        "/clients/{client_id}/": {
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
                    "oidc_provider"
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
        "/openid/authorize": {
            "get": {
                "description": "Example: ``` GET https://localhost:8000/authorize?client_id=<your-client-id>&response_type=code+id_token&scope=openid+email&redirect_uri=<your-redirect-uri>&state=0123456789 ``` This endpoint is compatible with OpenID Connect and also supports the POST method, in which case the parameters are passed as a form post.\\nSee also:\\n  - [OAuth 2.0 Authorization Endpoint](http://tools.ietf.org/html/rfc6749#section-3.1)\\n  - [OIDC Authentication request](http://openid.net/specs/openid-connect-core-1_0.html#AuthRequest)\\n  - [OIDC Successful Authentication response](http://openid.net/specs/openid-connect-core-1_0.html#AuthResponse)\\n  - [OIDC Error Authentication response](http://openid.net/specs/openid-connect-core-1_0.html#AuthError)\\n", 
                "externalDocs": {
                    "description": "OpenID Authorization Endpoint", 
                    "url": "http://openid.net/specs/openid-connect-core-1_0.html#AuthorizationEndpoint"
                }, 
                "operationId": "authorize", 
                "parameters": [
                    {
                        "description": "A client ID obtained from the [Dashboard](https://localhost:8000/admin/).\\n", 
                        "in": "query", 
                        "name": "client_id", 
                        "required": true, 
                        "type": "string"
                    }, 
                    {
                        "description": "The OIDC response type to use for this authentication flow. Valid choices are `code`, `id_token`, `token`, `token id_token`, `code id_token` `code token` and `code token id_token`, but a client can be configured with a more restricted set.\\n", 
                        "in": "query", 
                        "name": "response_type", 
                        "required": true, 
                        "type": "string"
                    }, 
                    {
                        "description": "The space-separated identity claims to request from the end-user. Always include `openid` as a scope for compatibility with OIDC.\\n", 
                        "in": "query", 
                        "name": "scope", 
                        "required": true, 
                        "type": "string"
                    }, 
                    {
                        "description": "The location to redirect to after (un)successful authentication. See OIDC for the parameters passed in the query string (`response_mode=query`) or as fragments (`response_mode=fragment`). This must be one of the registered redirect URLs.\\n", 
                        "in": "query", 
                        "name": "redirect_uri", 
                        "required": true, 
                        "type": "string"
                    }, 
                    {
                        "description": "An opaque string that will be passed back to the redirect URL and therefore can be used to communicate client side state and prevent CSRF attacks.\\n", 
                        "in": "query", 
                        "name": "state", 
                        "required": true, 
                        "type": "string"
                    }, 
                    {
                        "description": "Whether to append parameters to the redirect URL in the query string (`query`) or as fragments (`fragment`). This option usually has a sensible default for each of the response types.\\n", 
                        "in": "query", 
                        "name": "response_mode", 
                        "required": false, 
                        "type": "string"
                    }, 
                    {
                        "description": "An nonce provided by the client that will be included in any ID Token generated for this session. Clients should use the nonce to mitigate replay attacks.\\n", 
                        "in": "query", 
                        "name": "nonce", 
                        "required": false, 
                        "type": "string"
                    }, 
                    {
                        "default": "page", 
                        "description": "The authentication display mode, which can be one of `page`, `popup` or `modal`. Defaults to `page`.\\n", 
                        "in": "query", 
                        "name": "display", 
                        "required": false, 
                        "type": "string"
                    }, 
                    {
                        "default": "login", 
                        "description": "Space-delimited, case sensitive list of ASCII string values that specifies whether the Authorization Server prompts the End-User for re-authentication and consent. The supported values are: `none`, `login`, `consent`. If `consent` the end-user is asked to (re)confirm what claims they share. Use `none` to check for an active session.\\n", 
                        "in": "query", 
                        "name": "prompt", 
                        "required": false, 
                        "type": "string"
                    }, 
                    {
                        "default": 0, 
                        "description": "Specifies the allowable elapsed time in seconds since the last time the end-user was actively authenticated.\\n", 
                        "in": "query", 
                        "name": "max_age", 
                        "required": false, 
                        "type": "integer"
                    }, 
                    {
                        "description": "Specifies the preferred language to use on the authorization page, as a space-separated list of BCP47 language tags. Ignored at the moment.\\n", 
                        "in": "query", 
                        "name": "ui_locales", 
                        "required": false, 
                        "type": "string"
                    }
                ], 
                "responses": {
                    "302": {
                        "description": "A successful or erroneous authentication response.\\n"
                    }, 
                    "303": {
                        "description": "Sign in with page, popup or modal.\\n"
                    }
                }, 
                "summary": "Authenticate a user", 
                "tags": [
                    "experimental", 
                    "Authentication"
                ]
            }
        }, 
        "/openid/token": {
            "post": {
                "description": "Exchange an authorization code for an ID Token or Access Token.\\nThis endpoint supports both `client_secret_post` and `client_secret_basic` authentication methods, as specified by the clients `token_endpoint_auth_method`.\\nSee also:\\n  - [OIDC Token Endpoint](http://openid.net/specs/openid-connect-core-1_0.html#TokenRequest)\\n  - [OIDC Successful Token response](http://openid.net/specs/openid-connect-core-1_0.html#TokenResponse)\\n  - [OIDC Token Error response](http://openid.net/specs/openid-connect-core-1_0.html#TokenError)\\n", 
                "externalDocs": {
                    "description": "OpenID Token Endpoint", 
                    "url": "http://openid.net/specs/openid-connect-core-1_0.html#TokenEndpoint"
                }, 
                "operationId": "token", 
                "parameters": [
                    {
                        "description": "HTTP Basic authorization header.\\n", 
                        "in": "header", 
                        "name": "Authorization", 
                        "required": false, 
                        "type": "string"
                    }, 
                    {
                        "in": "body", 
                        "name": "content", 
                        "schema": {
                            "properties": {
                                "client_id": {
                                    "description": "The registered client ID.\\n", 
                                    "type": "string"
                                }, 
                                "client_secret": {
                                    "description": "The registered client ID secret.\\n", 
                                    "format": "password", 
                                    "type": "string"
                                }, 
                                "code": {
                                    "description": "The authorization code previously obtained from the Authentication endpoint.\\n", 
                                    "type": "string"
                                }, 
                                "grant_type": {
                                    "description": "The authorization grant type, must be `authorization_code`.\\n", 
                                    "type": "string"
                                }, 
                                "redirect_uri": {
                                    "description": "The redirect URL that was used previously with the Authentication endpoint.\\n", 
                                    "type": "string"
                                }
                            }, 
                            "required": [
                                "client_id"
                            ], 
                            "type": "object"
                        }
                    }
                ], 
                "produces": [
                    "application/json"
                ], 
                "responses": {
                    "200": {
                        "$ref": "#/responses/Token", 
                        "x-scope": [
                            ""
                        ]
                    }, 
                    "400": {
                        "$ref": "#/responses/OAuth2Error", 
                        "x-scope": [
                            ""
                        ]
                    }, 
                    "401": {
                        "$ref": "#/responses/OAuth2Error", 
                        "x-scope": [
                            ""
                        ]
                    }
                }, 
                "summary": "Obtain an ID Token", 
                "tags": [
                    "experimental", 
                    "Authentication"
                ]
            }
        }, 
        "/openid/userinfo": {
            "get": {
                "description": "Use this endpoint to retrieve a users profile in case youve not already obtained enough details from the ID Token via the Token Endpoint.\\n See also:\\n - [OIDC UserInfo endpoint](http://openid.net/specs/openid-connect-core-1_0.html#UserInfo)\\n", 
                "operationId": "userInfo", 
                "produces": [
                    "application/json"
                ], 
                "responses": {
                    "200": {
                        "$ref": "#/responses/UserInfo", 
                        "x-scope": [
                            ""
                        ]
                    }, 
                    "401": {
                        "$ref": "#/responses/OAuth2Error", 
                        "x-scope": [
                            ""
                        ]
                    }, 
                    "default": {
                        "$ref": "#/responses/OAuth2Error", 
                        "x-scope": [
                            ""
                        ]
                    }
                }, 
                "security": [
                    {
                        "oauth_code": [
                            "oidc", 
                            "email", 
                            "phone", 
                            "address", 
                            "ge:roles", 
                            "ge:site"
                        ]
                    }, 
                    {
                        "oauth_implicit": [
                            "oidc", 
                            "email", 
                            "phone", 
                            "address", 
                            "ge:roles", 
                            "ge:site"
                        ]
                    }
                ], 
                "summary": "Retrieve their user profile", 
                "tags": [
                    "experimental", 
                    "Authentication"
                ]
            }
        }, 
        "/users/": {
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
                    "oidc_provider"
                ]
            }
        }, 
        "/users/{user_id}/": {
            "delete": {
                "operationId": "user_delete", 
                "responses": {
                    "204": {
                        "description": ""
                    }
                }, 
                "tags": [
                    "oidc_provider"
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
                    "oidc_provider"
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
                    "oidc_provider"
                ]
            }
        }
    }, 
    "responses": {
        "OAuth2Error": {
            "description": "OAuth 2.0 error response", 
            "schema": {
                "$ref": "#/definitions/OAuth2Error", 
                "x-scope": [
                    "", 
                    "#/responses/OAuth2Error"
                ]
            }
        }, 
        "ProblemDetail": {
            "description": "Problem Detail error response", 
            "schema": {
                "$ref": "#/definitions/ProblemDetail", 
                "x-scope": [
                    ""
                ]
            }
        }, 
        "Token": {
            "description": "Token response", 
            "schema": {
                "$ref": "#/definitions/Token", 
                "x-scope": [
                    "", 
                    "#/responses/Token"
                ]
            }
        }, 
        "UserInfo": {
            "description": "UserInfo response", 
            "schema": {
                "$ref": "#/definitions/UserInfo", 
                "x-scope": [
                    "", 
                    "#/responses/UserInfo"
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
        }, 
        "OAuth2": {
            "authorizationUrl": "http://localhost:8000/openid/authorize", 
            "flow": "accessCode", 
            "scopes": {
                "roles": "Grants access to user roles", 
                "site": "Grants access to site-specific data"
            }, 
            "tokenUrl": "http:///localhost:8000/openid/token", 
            "type": "oauth2"
        }, 
        "client_registration_token": {
            "description": "Client management via registration token.", 
            "in": "header", 
            "name": "Authorization", 
            "type": "apiKey"
        }, 
        "client_secret": {
            "description": "Session management by confidential clients.", 
            "flow": "password", 
            "scopes": {
                "clients": "Enable client management"
            }, 
            "tokenUrl": "http://localhost:8000/openid/token", 
            "type": "oauth2"
        }, 
        "oauth_code": {
            "authorizationUrl": "http://locahost:8000/authorize", 
            "description": "End-user authentication.", 
            "flow": "accessCode", 
            "scopes": {
                "address": "The users postal address", 
                "email": "The users email address", 
                "ge:roles": "The users roles", 
                "ge:site": "The users site-specific data", 
                "oidc": "Enable OIDC flow", 
                "phone": "The users phone number"
            }, 
            "tokenUrl": "http://locahost:8000/token", 
            "type": "oauth2"
        }, 
        "oauth_implicit": {
            "authorizationUrl": "http://localhost:8000/authorize", 
            "description": "End-user authentication.", 
            "flow": "implicit", 
            "scopes": {
                "address": "The users postal address", 
                "email": "The users email address", 
                "ge:roles": "The users roles", 
                "ge:site": "The users site-specific data", 
                "oidc": "Enable OIDC flow", 
                "phone": "The users phone number"
            }, 
            "type": "oauth2"
        }, 
        "user_jwt": {
            "description": "Session management by Authentiq ID.", 
            "flow": "application", 
            "scopes": {
                "session": "Enable session management"
            }, 
            "tokenUrl": "http://localhost:8000/openid/token", 
            "type": "oauth2"
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
