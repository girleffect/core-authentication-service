import logging

from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from oidc_provider.models import Client

from authentication_service.api.stubs import AbstractStubClass
from authentication_service.models import CoreUser
from authentication_service.utils import set_listing_limit, \
    strip_empty_optional_fields

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

    @staticmethod
    def client_list(request, offset=None, limit=None, client_ids=None,
                    client_token_id=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param offset (optional): integer An optional query parameter specifying the offset in the result set to start from.
        :param limit (optional): integer An optional query parameter to limit the number of results returned.
        :param client_ids (optional): string An optional query parameter to filter by a list of client.id.
        :param clent_token_id (optional): string An optional query parameter to filter by a single client.client_id.
        """
        offset = int(offset if offset else settings.DEFAULT_LISTING_OFFSET)
        limit = set_listing_limit(limit)

        clients = Client.objects.values(*CLIENT_VALUES)

        if client_ids:
            clients = clients.filter(id__in=client_ids)

        if client_token_id:
            clients = clients.filter(client_id=client_token_id)

        clients = clients[offset:limit]
        return list(clients)


    @staticmethod
    def client_read(request, client_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param client_id: string A string value identifying the client
        """
        result = Client.objects.filter(
            client_id=client_id).values(*CLIENT_VALUES).get()
        return result

    @staticmethod
    def user_list(request, offset=None, limit=None, email=None,
                  username_prefix=None, user_ids=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        """
        offset = int(offset if offset else settings.DEFAULT_LISTING_OFFSET)
        limit = set_listing_limit(limit)

        users = CoreUser.objects.values(*USER_VALUES)

        if user_ids:
            users = users.filter(id__in=user_ids)
        if email:
            users = users.filter(email=email)
        if username_prefix:
            users = users.filter(username__startswith=username_prefix)

        users = users[offset:limit]
        result = []
        for user in list(users):
            result.append(strip_empty_optional_fields(user))
        return result

    @staticmethod
    def user_delete(request, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        user = CoreUser.objects.filter(id=user_id)
        result = strip_empty_optional_fields(user.values(*USER_VALUES).get())
        user.delete()  # Delete user after stripping fields
        return result


    @staticmethod
    def user_read(request, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        result = strip_empty_optional_fields(
            CoreUser.objects.filter(id=user_id).values(*USER_VALUES).get())
        return result

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
        result = {}
        for field in instance._meta.fields:
            if field.name in USER_VALUES:
                if field.name == "avatar":  # Prevent serialization issue
                    result[field.name] = instance.avatar.path
                else:
                    result[field.name] = getattr(instance, field.name)
        return strip_empty_optional_fields(result)
