import logging

from django.conf import settings
from django.db.models.expressions import RawSQL
from django.forms import model_to_dict
from django.http import Http404
from django.shortcuts import get_object_or_404
from oidc_provider.models import Client

from authentication_service.api.stubs import AbstractStubClass
from authentication_service.models import CoreUser
from authentication_service.utils import strip_empty_optional_fields, \
    check_limit, to_dict_with_custom_fields

LOGGER = logging.getLogger(__name__)

CLIENT_VALUES = [
    "id", "_post_logout_redirect_uris", "_redirect_uris", "client_id",
    "contact_email", "logo", "name", "require_consent", "response_type",
    "reuse_consent", "terms_url", "website_url"
]
USER_VALUES = [
    "id", "username", "first_name", "last_name", "email", "is_active",
    "date_joined", "last_login", "email_verified", "msisdn_verified", "msisdn",
    "gender", "birth_date", "avatar", "country", "created_at", "updated_at"
]


class Implementation(AbstractStubClass):

    # client_list -- Synchronisation point for meld
    @staticmethod
    def client_list(request, offset=None, limit=None, client_ids=None, client_token_id=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param offset (optional): integer An optional query parameter specifying the offset in the result set to start from.
        :param limit (optional): integer An optional query parameter to limit the number of results returned.
        :param client_ids (optional): string An optional query parameter to filter by a list of client.id.
        :param clent_token_id (optional): string An optional query parameter to filter by a single client.client_id.
        """
        offset = int(offset if offset else settings.DEFAULT_LISTING_OFFSET)
        limit = check_limit(limit)

        clients = Client.objects.values(*CLIENT_VALUES).order_by("id")

        if client_ids:
            clients = clients.filter(id__in=client_ids)

        if client_token_id:
            clients = clients.filter(client_id=client_token_id)

        clients = clients.annotate(
            x_total_count=RawSQL("COUNT(*) OVER ()", [])
        )[offset:offset + limit]
        return (
            [strip_empty_optional_fields(client) for client in clients],
            {
                "X-Total-Count": clients[0][
                    "x_total_count"] if len(clients) > 0 else 0
            }
        )


    # client_read -- Synchronisation point for meld
    @staticmethod
    def client_read(request, client_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param client_id: string A string value identifying the client
        """
        client = get_object_or_404(Client, client_id=client_id)
        result = to_dict_with_custom_fields(client, CLIENT_VALUES)
        return strip_empty_optional_fields(result)

    # user_list -- Synchronisation point for meld
    @staticmethod
    def user_list(request, offset=None, limit=None, email=None,
                  username_prefix=None, user_ids=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        """
        offset = int(offset if offset else settings.DEFAULT_LISTING_OFFSET)
        limit = check_limit(limit)

        users = CoreUser.objects.values(*USER_VALUES).order_by("id")

        if user_ids:
            users = users.filter(id__in=user_ids)
        if email:
            users = users.filter(email=email)
        if username_prefix:
            users = users.filter(username__startswith=username_prefix)

        users = users.annotate(
            x_total_count=RawSQL("COUNT(*) OVER ()", [])
        )[offset:offset + limit]
        return (
            [strip_empty_optional_fields(user) for user in users],
            {
                "X-Total-Count": clients[0][
                    "x_total_count"] if len(user) > 0 else 0
            }
        )

    # user_delete -- Synchronisation point for meld
    @staticmethod
    def user_delete(request, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        user = get_object_or_404(CoreUser, id=user_id)
        result = to_dict_with_custom_fields(user, USER_VALUES)
        user.delete()
        return strip_empty_optional_fields(result)

    # user_read -- Synchronisation point for meld
    @staticmethod
    def user_read(request, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        user = get_object_or_404(CoreUser, id=user_id)
        result = to_dict_with_custom_fields(user, USER_VALUES)
        return strip_empty_optional_fields(result)

    # user_update -- Synchronisation point for meld
    @staticmethod
    def user_update(request, body, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param body: dict A dictionary containing the parsed and validated body
        :param user_id: string A UUID value identifying the user.
        """
        instance = get_object_or_404(CoreUser, id=user_id)
        for attr, value in body.items():
            try:
                setattr(instance, attr, value)
            except Exception as e:
                LOGGER.error("Failed to set user attribute %s: %s" % (attr, e))

        instance.save()
        result = to_dict_with_custom_fields(instance, USER_VALUES)
        return strip_empty_optional_fields(result)
