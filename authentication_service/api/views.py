"""
Do not modify this file. It is generated from the Swagger specification.

"""
import importlib
import logging
import json
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


def maybe_validate_result(result_string, schema):
    if VALIDATE_RESPONSES:
        try:
            utils.validate(json.loads(result_string, encoding="utf8"), schema)
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
        try:

            # offset (optional): integer An optional query parameter specifying the offset in the result set to start from.
            offset = request.GET.get("offset", None)
            if offset is not None:
                offset = int(offset)
                schema = {'type': 'integer', 'default': 0, 'minimum': 0}
                utils.validate(offset, schema)
            # limit (optional): integer An optional query parameter to limit the number of results returned.
            limit = request.GET.get("limit", None)
            if limit is not None:
                limit = int(limit)
                schema = {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 20}
                utils.validate(limit, schema)
            # client_ids (optional): array An optional list of client ids
            client_ids = request.GET.get("client_ids", None)
            if client_ids is not None:
                client_ids = client_ids.split(",")
                if client_ids:
                    client_ids = [int(e) for e in client_ids]
            if client_ids is not None:
                schema = {'type': 'array', 'items': {'type': 'integer'}, 'minItems': 1, 'uniqueItems': True}
                utils.validate(client_ids, schema)
            # client_token_id (optional): string An optional client id to filter on. This is not the primary key.
            client_token_id = request.GET.get("client_token_id", None)
            if client_token_id is not None:
                schema = {'type': 'string'}
                utils.validate(client_token_id, schema)
            result = Stubs.client_list(request, offset, limit, client_ids, client_token_id, )

            if type(result) is tuple:
                result, headers = result
            else:
                headers = {}

            # The result may contain fields with date or datetime values that will not
            # pass JSON validation. We first create the response, and then maybe validate
            # the response content against the schema.
            response = JsonResponse(result, safe=False)

            maybe_validate_result(response.content, self.GET_RESPONSE_SCHEMA)

            for key, val in headers.items():
                response[key] = val

            return response
        except ValidationError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve.message))
        except ValueError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve))


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
        try:

            result = Stubs.client_read(request, client_id, )

            if type(result) is tuple:
                result, headers = result
            else:
                headers = {}

            # The result may contain fields with date or datetime values that will not
            # pass JSON validation. We first create the response, and then maybe validate
            # the response content against the schema.
            response = JsonResponse(result, safe=False)

            maybe_validate_result(response.content, self.GET_RESPONSE_SCHEMA)

            for key, val in headers.items():
                response[key] = val

            return response
        except ValidationError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve.message))
        except ValueError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve))


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(utils.login_required_no_redirect, name="get")
class Countries(View):

    GET_RESPONSE_SCHEMA = json.loads("""{
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

    def get(self, request, *args, **kwargs):
        """
        :param self: A Countries instance
        :param request: An HttpRequest
        """
        try:

            # offset (optional): integer An optional query parameter specifying the offset in the result set to start from.
            offset = request.GET.get("offset", None)
            if offset is not None:
                offset = int(offset)
                schema = {'type': 'integer', 'default': 0, 'minimum': 0}
                utils.validate(offset, schema)
            # limit (optional): integer An optional query parameter to limit the number of results returned.
            limit = request.GET.get("limit", None)
            if limit is not None:
                limit = int(limit)
                schema = {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 20}
                utils.validate(limit, schema)
            # country_codes (optional): array An optional list of country codes
            country_codes = request.GET.get("country_codes", None)
            if country_codes is not None:
                country_codes = country_codes.split(",")
            if country_codes is not None:
                schema = {'type': 'array', 'items': {'type': 'string', 'minLength': 2, 'maxLength': 2}, 'minItems': 1, 'uniqueItems': True}
                utils.validate(country_codes, schema)
            result = Stubs.country_list(request, offset, limit, country_codes, )

            if type(result) is tuple:
                result, headers = result
            else:
                headers = {}

            # The result may contain fields with date or datetime values that will not
            # pass JSON validation. We first create the response, and then maybe validate
            # the response content against the schema.
            response = JsonResponse(result, safe=False)

            maybe_validate_result(response.content, self.GET_RESPONSE_SCHEMA)

            for key, val in headers.items():
                response[key] = val

            return response
        except ValidationError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve.message))
        except ValueError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve))


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(utils.login_required_no_redirect, name="get")
class CountriesCountryCode(View):

    GET_RESPONSE_SCHEMA = schemas.country

    def get(self, request, country_code, *args, **kwargs):
        """
        :param self: A CountriesCountryCode instance
        :param request: An HttpRequest
        :param country_code: string A string value identifying the country
        """
        try:

            result = Stubs.country_read(request, country_code, )

            if type(result) is tuple:
                result, headers = result
            else:
                headers = {}

            # The result may contain fields with date or datetime values that will not
            # pass JSON validation. We first create the response, and then maybe validate
            # the response content against the schema.
            response = JsonResponse(result, safe=False)

            maybe_validate_result(response.content, self.GET_RESPONSE_SCHEMA)

            for key, val in headers.items():
                response[key] = val

            return response
        except ValidationError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve.message))
        except ValueError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve))


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(utils.login_required_no_redirect, name="get")
class InvitationsInvitationIdSend(View):

    GET_RESPONSE_SCHEMA = schemas.__UNSPECIFIED__

    def get(self, request, invitation_id, *args, **kwargs):
        """
        :param self: A InvitationsInvitationIdSend instance
        :param request: An HttpRequest
        :param invitation_id: string 
        """
        try:

            # language (optional): string 
            language = request.GET.get("language", None)
            if language is not None:
                schema = {'type': 'string', 'default': 'en'}
                utils.validate(language, schema)
            result = Stubs.invitation_send(request, invitation_id, language, )

            if type(result) is tuple:
                result, headers = result
            else:
                headers = {}

            # The result may contain fields with date or datetime values that will not
            # pass JSON validation. We first create the response, and then maybe validate
            # the response content against the schema.
            response = JsonResponse(result, safe=False)

            maybe_validate_result(response.content, self.GET_RESPONSE_SCHEMA)

            for key, val in headers.items():
                response[key] = val

            return response
        except ValidationError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve.message))
        except ValueError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve))


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(utils.login_required_no_redirect, name="get")
class InvitationsPurgeExpired(View):

    GET_RESPONSE_SCHEMA = schemas.__UNSPECIFIED__

    def get(self, request, *args, **kwargs):
        """
        :param self: A InvitationsPurgeExpired instance
        :param request: An HttpRequest
        """
        try:

            # cutoff_date (optional): string An optional cutoff date to purge invites before this date
            cutoff_date = request.GET.get("cutoff_date", None)
            if cutoff_date is not None:
                schema = {'type': 'string', 'format': 'date'}
                utils.validate(cutoff_date, schema)
            result = Stubs.purge_expired_invitations(request, cutoff_date, )

            if type(result) is tuple:
                result, headers = result
            else:
                headers = {}

            # The result may contain fields with date or datetime values that will not
            # pass JSON validation. We first create the response, and then maybe validate
            # the response content against the schema.
            response = JsonResponse(result, safe=False)

            maybe_validate_result(response.content, self.GET_RESPONSE_SCHEMA)

            for key, val in headers.items():
                response[key] = val

            return response
        except ValidationError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve.message))
        except ValueError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve))


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(utils.login_required_no_redirect, name="get")
@method_decorator(utils.login_required_no_redirect, name="post")
class Organisations(View):

    GET_RESPONSE_SCHEMA = json.loads("""{
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
    POST_RESPONSE_SCHEMA = schemas.organisation
    POST_BODY_SCHEMA = schemas.organisation_create

    def get(self, request, *args, **kwargs):
        """
        :param self: A Organisations instance
        :param request: An HttpRequest
        """
        try:

            # offset (optional): integer An optional query parameter specifying the offset in the result set to start from.
            offset = request.GET.get("offset", None)
            if offset is not None:
                offset = int(offset)
                schema = {'type': 'integer', 'default': 0, 'minimum': 0}
                utils.validate(offset, schema)
            # limit (optional): integer An optional query parameter to limit the number of results returned.
            limit = request.GET.get("limit", None)
            if limit is not None:
                limit = int(limit)
                schema = {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 20}
                utils.validate(limit, schema)
            # organisation_ids (optional): array An optional list of organisation ids
            organisation_ids = request.GET.get("organisation_ids", None)
            if organisation_ids is not None:
                organisation_ids = organisation_ids.split(",")
                if organisation_ids:
                    organisation_ids = [int(e) for e in organisation_ids]
            if organisation_ids is not None:
                schema = {'type': 'array', 'items': {'type': 'integer'}, 'minItems': 1, 'uniqueItems': True}
                utils.validate(organisation_ids, schema)
            result = Stubs.organisation_list(request, offset, limit, organisation_ids, )

            if type(result) is tuple:
                result, headers = result
            else:
                headers = {}

            # The result may contain fields with date or datetime values that will not
            # pass JSON validation. We first create the response, and then maybe validate
            # the response content against the schema.
            response = JsonResponse(result, safe=False)

            maybe_validate_result(response.content, self.GET_RESPONSE_SCHEMA)

            for key, val in headers.items():
                response[key] = val

            return response
        except ValidationError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve.message))
        except ValueError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve))

    def post(self, request, *args, **kwargs):
        """
        :param self: A Organisations instance
        :param request: An HttpRequest
        """
        body = utils.body_to_dict(request.body, self.POST_BODY_SCHEMA)
        if not body:
            return HttpResponseBadRequest("Body required")

        try:

            result = Stubs.organisation_create(request, body, )

            if type(result) is tuple:
                result, headers = result
            else:
                headers = {}

            # The result may contain fields with date or datetime values that will not
            # pass JSON validation. We first create the response, and then maybe validate
            # the response content against the schema.
            response = JsonResponse(result, safe=False)

            maybe_validate_result(response.content, self.POST_RESPONSE_SCHEMA)

            for key, val in headers.items():
                response[key] = val

            return response
        except ValidationError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve.message))
        except ValueError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve))


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(utils.login_required_no_redirect, name="delete")
@method_decorator(utils.login_required_no_redirect, name="get")
@method_decorator(utils.login_required_no_redirect, name="put")
class OrganisationsOrganisationId(View):

    DELETE_RESPONSE_SCHEMA = schemas.__UNSPECIFIED__
    GET_RESPONSE_SCHEMA = schemas.organisation
    PUT_RESPONSE_SCHEMA = schemas.organisation
    PUT_BODY_SCHEMA = schemas.organisation_update

    def delete(self, request, organisation_id, *args, **kwargs):
        """
        :param self: A OrganisationsOrganisationId instance
        :param request: An HttpRequest
        :param organisation_id: integer An integer identifying an organisation a user belongs to
        """
        try:

            result = Stubs.organisation_delete(request, organisation_id, )

            if type(result) is tuple:
                result, headers = result
            else:
                headers = {}

            # The result may contain fields with date or datetime values that will not
            # pass JSON validation. We first create the response, and then maybe validate
            # the response content against the schema.
            response = JsonResponse(result, safe=False)

            maybe_validate_result(response.content, self.DELETE_RESPONSE_SCHEMA)

            for key, val in headers.items():
                response[key] = val

            return response
        except ValidationError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve.message))
        except ValueError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve))

    def get(self, request, organisation_id, *args, **kwargs):
        """
        :param self: A OrganisationsOrganisationId instance
        :param request: An HttpRequest
        :param organisation_id: integer An integer identifying an organisation a user belongs to
        """
        try:

            result = Stubs.organisation_read(request, organisation_id, )

            if type(result) is tuple:
                result, headers = result
            else:
                headers = {}

            # The result may contain fields with date or datetime values that will not
            # pass JSON validation. We first create the response, and then maybe validate
            # the response content against the schema.
            response = JsonResponse(result, safe=False)

            maybe_validate_result(response.content, self.GET_RESPONSE_SCHEMA)

            for key, val in headers.items():
                response[key] = val

            return response
        except ValidationError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve.message))
        except ValueError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve))

    def put(self, request, organisation_id, *args, **kwargs):
        """
        :param self: A OrganisationsOrganisationId instance
        :param request: An HttpRequest
        :param organisation_id: integer An integer identifying an organisation a user belongs to
        """
        body = utils.body_to_dict(request.body, self.PUT_BODY_SCHEMA)
        if not body:
            return HttpResponseBadRequest("Body required")

        try:

            result = Stubs.organisation_update(request, body, organisation_id, )

            if type(result) is tuple:
                result, headers = result
            else:
                headers = {}

            # The result may contain fields with date or datetime values that will not
            # pass JSON validation. We first create the response, and then maybe validate
            # the response content against the schema.
            response = JsonResponse(result, safe=False)

            maybe_validate_result(response.content, self.PUT_RESPONSE_SCHEMA)

            for key, val in headers.items():
                response[key] = val

            return response
        except ValidationError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve.message))
        except ValueError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve))


@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(utils.login_required_no_redirect, name="post")
class RequestUserDeletion(View):

    POST_RESPONSE_SCHEMA = schemas.__UNSPECIFIED__
    POST_BODY_SCHEMA = schemas.request_user_deletion

    def post(self, request, *args, **kwargs):
        """
        :param self: A RequestUserDeletion instance
        :param request: An HttpRequest
        """
        body = utils.body_to_dict(request.body, self.POST_BODY_SCHEMA)
        if not body:
            return HttpResponseBadRequest("Body required")

        try:

            result = Stubs.request_user_deletion(request, body, )

            if type(result) is tuple:
                result, headers = result
            else:
                headers = {}

            # The result may contain fields with date or datetime values that will not
            # pass JSON validation. We first create the response, and then maybe validate
            # the response content against the schema.
            response = JsonResponse(result, safe=False)

            maybe_validate_result(response.content, self.POST_RESPONSE_SCHEMA)

            for key, val in headers.items():
                response[key] = val

            return response
        except ValidationError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve.message))
        except ValueError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve))


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

    def get(self, request, *args, **kwargs):
        """
        :param self: A Users instance
        :param request: An HttpRequest
        """
        try:

            # offset (optional): integer An optional query parameter specifying the offset in the result set to start from.
            offset = request.GET.get("offset", None)
            if offset is not None:
                offset = int(offset)
                schema = {'type': 'integer', 'default': 0, 'minimum': 0}
                utils.validate(offset, schema)
            # limit (optional): integer An optional query parameter to limit the number of results returned.
            limit = request.GET.get("limit", None)
            if limit is not None:
                limit = int(limit)
                schema = {'type': 'integer', 'minimum': 1, 'maximum': 100, 'default': 20}
                utils.validate(limit, schema)
            # birth_date (optional): string An optional birth_date range filter
            birth_date = request.GET.get("birth_date", None)
            if birth_date is not None:
                schema = {'type': 'string'}
                utils.validate(birth_date, schema)
            # country (optional): string An optional country filter
            country = request.GET.get("country", None)
            if country is not None:
                schema = {'type': 'string', 'minLength': 2, 'maxLength': 2}
                utils.validate(country, schema)
            # date_joined (optional): string An optional date joined range filter
            date_joined = request.GET.get("date_joined", None)
            if date_joined is not None:
                schema = {'type': 'string'}
                utils.validate(date_joined, schema)
            # email (optional): string An optional case insensitive email inner match filter
            email = request.GET.get("email", None)
            if email is not None:
                schema = {'type': 'string', 'minLength': 3}
                utils.validate(email, schema)
            # email_verified (optional): boolean An optional email verified filter
            email_verified = request.GET.get("email_verified", None)
            if email_verified is not None:
                email_verified = (email_verified.lower() == "true")
                schema = {'type': 'boolean'}
                utils.validate(email_verified, schema)
            # first_name (optional): string An optional case insensitive first name inner match filter
            first_name = request.GET.get("first_name", None)
            if first_name is not None:
                schema = {'type': 'string', 'minLength': 3}
                utils.validate(first_name, schema)
            # gender (optional): string An optional gender filter
            gender = request.GET.get("gender", None)
            if gender is not None:
                schema = {'type': 'string'}
                utils.validate(gender, schema)
            # is_active (optional): boolean An optional is_active filter
            is_active = request.GET.get("is_active", None)
            if is_active is not None:
                is_active = (is_active.lower() == "true")
                schema = {'type': 'boolean'}
                utils.validate(is_active, schema)
            # last_login (optional): string An optional last login range filter
            last_login = request.GET.get("last_login", None)
            if last_login is not None:
                schema = {'type': 'string'}
                utils.validate(last_login, schema)
            # last_name (optional): string An optional case insensitive last name inner match filter
            last_name = request.GET.get("last_name", None)
            if last_name is not None:
                schema = {'type': 'string', 'minLength': 3}
                utils.validate(last_name, schema)
            # msisdn (optional): string An optional case insensitive MSISDN inner match filter
            msisdn = request.GET.get("msisdn", None)
            if msisdn is not None:
                schema = {'type': 'string', 'minLength': 3}
                utils.validate(msisdn, schema)
            # msisdn_verified (optional): boolean An optional MSISDN verified filter
            msisdn_verified = request.GET.get("msisdn_verified", None)
            if msisdn_verified is not None:
                msisdn_verified = (msisdn_verified.lower() == "true")
                schema = {'type': 'boolean'}
                utils.validate(msisdn_verified, schema)
            # nickname (optional): string An optional case insensitive nickname inner match filter
            nickname = request.GET.get("nickname", None)
            if nickname is not None:
                schema = {'type': 'string', 'minLength': 3}
                utils.validate(nickname, schema)
            # organisation_id (optional): integer An optional filter on the organisation id
            organisation_id = request.GET.get("organisation_id", None)
            if organisation_id is not None:
                organisation_id = int(organisation_id)
                schema = {'type': 'integer'}
                utils.validate(organisation_id, schema)
            # updated_at (optional): string An optional updated_at range filter
            updated_at = request.GET.get("updated_at", None)
            if updated_at is not None:
                schema = {'type': 'string'}
                utils.validate(updated_at, schema)
            # username (optional): string An optional case insensitive username inner match filter
            username = request.GET.get("username", None)
            if username is not None:
                schema = {'type': 'string', 'minLength': 3}
                utils.validate(username, schema)
            # q (optional): string An optional case insensitive inner match filter across all searchable text fields
            q = request.GET.get("q", None)
            if q is not None:
                schema = {'type': 'string', 'minLength': 3}
                utils.validate(q, schema)
            # tfa_enabled (optional): boolean An optional filter based on whether a user has 2FA enabled or not
            tfa_enabled = request.GET.get("tfa_enabled", None)
            if tfa_enabled is not None:
                tfa_enabled = (tfa_enabled.lower() == "true")
                schema = {'type': 'boolean'}
                utils.validate(tfa_enabled, schema)
            # has_organisation (optional): boolean An optional filter based on whether a user belongs to an organisation or not
            has_organisation = request.GET.get("has_organisation", None)
            if has_organisation is not None:
                has_organisation = (has_organisation.lower() == "true")
                schema = {'type': 'boolean'}
                utils.validate(has_organisation, schema)
            # order_by (optional): array Fields and directions to order by, e.g. "-created_at,username". Add "-" in front of a field name to indicate descending order.
            order_by = request.GET.get("order_by", None)
            if order_by is not None:
                order_by = order_by.split(",")
            if order_by is not None:
                schema = {'type': 'array', 'items': {'type': 'string'}, 'uniqueItems': True}
                utils.validate(order_by, schema)
            # user_ids (optional): array An optional list of user ids
            user_ids = request.GET.get("user_ids", None)
            if user_ids is not None:
                user_ids = user_ids.split(",")
            if user_ids is not None:
                schema = {'type': 'array', 'items': {'type': 'string', 'format': 'uuid'}, 'minItems': 1, 'uniqueItems': True}
                utils.validate(user_ids, schema)
            # site_ids (optional): array An optional list of site ids
            site_ids = request.GET.get("site_ids", None)
            if site_ids is not None:
                site_ids = site_ids.split(",")
                if site_ids:
                    site_ids = [int(e) for e in site_ids]
            if site_ids is not None:
                schema = {'type': 'array', 'items': {'type': 'integer'}, 'minItems': 1, 'uniqueItems': True}
                utils.validate(site_ids, schema)
            result = Stubs.user_list(request, offset, limit, birth_date, country, date_joined, email, email_verified, first_name, gender, is_active, last_login, last_name, msisdn, msisdn_verified, nickname, organisation_id, updated_at, username, q, tfa_enabled, has_organisation, order_by, user_ids, site_ids, )

            if type(result) is tuple:
                result, headers = result
            else:
                headers = {}

            # The result may contain fields with date or datetime values that will not
            # pass JSON validation. We first create the response, and then maybe validate
            # the response content against the schema.
            response = JsonResponse(result, safe=False)

            maybe_validate_result(response.content, self.GET_RESPONSE_SCHEMA)

            for key, val in headers.items():
                response[key] = val

            return response
        except ValidationError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve.message))
        except ValueError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve))


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
        try:

            result = Stubs.user_delete(request, user_id, )

            if type(result) is tuple:
                result, headers = result
            else:
                headers = {}

            # The result may contain fields with date or datetime values that will not
            # pass JSON validation. We first create the response, and then maybe validate
            # the response content against the schema.
            response = JsonResponse(result, safe=False)

            maybe_validate_result(response.content, self.DELETE_RESPONSE_SCHEMA)

            for key, val in headers.items():
                response[key] = val

            return response
        except ValidationError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve.message))
        except ValueError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve))

    def get(self, request, user_id, *args, **kwargs):
        """
        :param self: A UsersUserId instance
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        try:

            result = Stubs.user_read(request, user_id, )

            if type(result) is tuple:
                result, headers = result
            else:
                headers = {}

            # The result may contain fields with date or datetime values that will not
            # pass JSON validation. We first create the response, and then maybe validate
            # the response content against the schema.
            response = JsonResponse(result, safe=False)

            maybe_validate_result(response.content, self.GET_RESPONSE_SCHEMA)

            for key, val in headers.items():
                response[key] = val

            return response
        except ValidationError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve.message))
        except ValueError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve))

    def put(self, request, user_id, *args, **kwargs):
        """
        :param self: A UsersUserId instance
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        body = utils.body_to_dict(request.body, self.PUT_BODY_SCHEMA)
        if not body:
            return HttpResponseBadRequest("Body required")

        try:

            result = Stubs.user_update(request, body, user_id, )

            if type(result) is tuple:
                result, headers = result
            else:
                headers = {}

            # The result may contain fields with date or datetime values that will not
            # pass JSON validation. We first create the response, and then maybe validate
            # the response content against the schema.
            response = JsonResponse(result, safe=False)

            maybe_validate_result(response.content, self.PUT_RESPONSE_SCHEMA)

            for key, val in headers.items():
                response[key] = val

            return response
        except ValidationError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve.message))
        except ValueError as ve:
            return HttpResponseBadRequest("Parameter validation failed: {}".format(ve))


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
        "country": {
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
            "type": "object"
        },
        "organisation": {
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
            "type": "object"
        },
        "organisation_create": {
            "properties": {
                "description": {
                    "type": "string"
                },
                "name": {
                    "type": "string"
                }
            },
            "required": [
                "name"
            ],
            "type": "object"
        },
        "organisation_update": {
            "minProperties": 1,
            "properties": {
                "description": {
                    "type": "string"
                },
                "name": {
                    "type": "string"
                }
            },
            "type": "object"
        },
        "request_user_deletion": {
            "properties": {
                "deleter_id": {
                    "format": "uuid",
                    "type": "string"
                },
                "reason": {
                    "type": "string"
                },
                "user_id": {
                    "format": "uuid",
                    "type": "string"
                }
            },
            "required": [
                "user_id",
                "deleter_id",
                "reason"
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
            "type": "object"
        },
        "user_site": {
            "properties": {
                "consented_at": {
                    "format": "date-time",
                    "type": "string"
                },
                "created_at": {
                    "format": "date-time",
                    "readOnly": true,
                    "type": "string"
                },
                "id": {
                    "type": "integer"
                },
                "site_id": {
                    "type": "integer"
                },
                "updated_at": {
                    "format": "date-time",
                    "readOnly": true,
                    "type": "string"
                },
                "user_id": {
                    "format": "uuid",
                    "type": "string"
                }
            },
            "required": [
                "id",
                "user_id",
                "site_id",
                "consented_at",
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
            "in": "path",
            "name": "client_id",
            "required": true,
            "type": "string"
        },
        "country_code": {
            "description": "A string value identifying the country",
            "in": "path",
            "maxLength": 2,
            "minLength": 2,
            "name": "country_code",
            "required": true,
            "type": "string"
        },
        "optional_cutoff_date": {
            "description": "An optional cutoff date to purge invites before this date",
            "format": "date",
            "in": "query",
            "name": "cutoff_date",
            "required": false,
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
        "organisation_id": {
            "description": "An integer identifying an organisation a user belongs to",
            "in": "path",
            "name": "organisation_id",
            "required": true,
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
                        "collectionFormat": "csv",
                        "description": "An optional list of client ids",
                        "in": "query",
                        "items": {
                            "type": "integer"
                        },
                        "minItems": 1,
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
                        "headers": {
                            "X-Total-Count": {
                                "description": "The total number of results matching the query",
                                "type": "integer"
                            }
                        },
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
        "/countries": {
            "get": {
                "operationId": "country_list",
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
                        "collectionFormat": "csv",
                        "description": "An optional list of country codes",
                        "in": "query",
                        "items": {
                            "maxLength": 2,
                            "minLength": 2,
                            "type": "string"
                        },
                        "minItems": 1,
                        "name": "country_codes",
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
                        "headers": {
                            "X-Total-Count": {
                                "description": "The total number of results matching the query",
                                "type": "integer"
                            }
                        },
                        "schema": {
                            "items": {
                                "$ref": "#/definitions/country",
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
        "/countries/{country_code}": {
            "get": {
                "operationId": "country_read",
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "",
                        "schema": {
                            "$ref": "#/definitions/country",
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
                    "$ref": "#/parameters/country_code",
                    "x-scope": [
                        ""
                    ]
                }
            ]
        },
        "/invitations/purge_expired": {
            "get": {
                "operationId": "purge_expired_invitations",
                "parameters": [
                    {
                        "$ref": "#/parameters/optional_cutoff_date",
                        "x-scope": [
                            ""
                        ]
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Began task to purge invitations."
                    },
                    "403": {
                        "description": "Forbidden"
                    }
                },
                "tags": [
                    "authentication"
                ]
            }
        },
        "/invitations/{invitation_id}/send": {
            "get": {
                "operationId": "invitation_send",
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "An invitation email was successfully queued for sending."
                    }
                },
                "tags": [
                    "authentication"
                ]
            },
            "parameters": [
                {
                    "format": "uuid",
                    "in": "path",
                    "name": "invitation_id",
                    "required": true,
                    "type": "string"
                },
                {
                    "default": "en",
                    "in": "query",
                    "name": "language",
                    "required": false,
                    "type": "string"
                }
            ]
        },
        "/organisations": {
            "get": {
                "operationId": "organisation_list",
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
                        "collectionFormat": "csv",
                        "description": "An optional list of organisation ids",
                        "in": "query",
                        "items": {
                            "type": "integer"
                        },
                        "minItems": 1,
                        "name": "organisation_ids",
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
                        "headers": {
                            "X-Total-Count": {
                                "description": "The total number of results matching the query",
                                "type": "integer"
                            }
                        },
                        "schema": {
                            "items": {
                                "$ref": "#/definitions/organisation",
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
            },
            "post": {
                "consumes": [
                    "application/json"
                ],
                "operationId": "organisation_create",
                "parameters": [
                    {
                        "in": "body",
                        "name": "data",
                        "schema": {
                            "$ref": "#/definitions/organisation_create",
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
                    "201": {
                        "description": "",
                        "schema": {
                            "$ref": "#/definitions/organisation",
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
        },
        "/organisations/{organisation_id}": {
            "delete": {
                "operationId": "organisation_delete",
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
                "operationId": "organisation_read",
                "produces": [
                    "application/json"
                ],
                "responses": {
                    "200": {
                        "description": "",
                        "schema": {
                            "$ref": "#/definitions/organisation",
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
                    "$ref": "#/parameters/organisation_id",
                    "x-scope": [
                        ""
                    ]
                }
            ],
            "put": {
                "consumes": [
                    "application/json"
                ],
                "operationId": "organisation_update",
                "parameters": [
                    {
                        "in": "body",
                        "name": "data",
                        "schema": {
                            "$ref": "#/definitions/organisation_update",
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
                            "$ref": "#/definitions/organisation",
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
        },
        "/request_user_deletion": {
            "post": {
                "consumes": [
                    "application/json"
                ],
                "operationId": "request_user_deletion",
                "parameters": [
                    {
                        "in": "body",
                        "name": "data",
                        "required": true,
                        "schema": {
                            "$ref": "#/definitions/request_user_deletion",
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
                        "description": "An optional filter on the organisation id",
                        "in": "query",
                        "name": "organisation_id",
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
                        "description": "An optional filter based on whether a user belongs to an organisation or not",
                        "in": "query",
                        "name": "has_organisation",
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
                        "collectionFormat": "csv",
                        "description": "An optional list of user ids",
                        "in": "query",
                        "items": {
                            "format": "uuid",
                            "type": "string"
                        },
                        "minItems": 1,
                        "name": "user_ids",
                        "required": false,
                        "type": "array",
                        "uniqueItems": true
                    },
                    {
                        "collectionFormat": "csv",
                        "description": "An optional list of site ids",
                        "in": "query",
                        "items": {
                            "type": "integer"
                        },
                        "minItems": 1,
                        "name": "site_ids",
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
                        "headers": {
                            "X-Total-Count": {
                                "description": "The total number of results matching the query",
                                "type": "integer"
                            }
                        },
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
