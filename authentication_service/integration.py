from django.conf import settings
from django.core.serializers import json, serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.forms import model_to_dict
from oidc_provider.models import Client

from authentication_service.api.stubs import AbstractStubClass
from authentication_service.models import CoreUser

CLIENT_VALUES = [
    "id", "_post_logout_redirect_uris", "_redirect_uris", "client_id",
    "contact_email", "logo", "name", "require_consent", "response_type",
    "reuse_consent", "terms_url", "website_url"
]
USER_VALUES = [
    "id", "username", "first_name", "last_name", "email", "is_active",
    "date_joined", "last_login", "email_verified", "msisdn_verified", "msisdn",
    "gender", "birth_date", "avatar", "country"
]


class Implementation(AbstractStubClass):

    @staticmethod
    def client_list(request, offset=None, limit=None, client_ids=None,
                    client_token_id=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param offset (optional): integer An optional query parameter specifying the offset in the result set to start from.
        :param limit (optional): integer An optional query parameter to limit the number of results returned.
        :param client_ids (optional): string An optional query parameter to filter by a list of client_ids.
        :param clent_token_id (optional): string An optional query parameter to filter by a single client_id.
        """
        if client_ids:
            result = [
                client for client in Client.objects.filter(
                    pk__in=client_ids).values(*CLIENT_VALUES)
            ]
        elif client_token_id:
            result = Client.objects.filter(
                client_id=client_token_id).values(*CLIENT_VALUES).get()
        else:
            result = [
                client for client in Client.objects.all().values(*CLIENT_VALUES)
            ]
        return result[int(offset if offset else 0):int(limit if limit else settings.DEFAULT_LISTING_LIMIT)]


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
        if email:
            result = [
                user for user in CoreUser.objects.filter(
                    email=email).values(*USER_VALUES)
            ]
        elif username_prefix:
            result = [
                user for user in CoreUser.objects.filter(
                    username__contains=username_prefix).values(*USER_VALUES)
            ]
        elif user_ids:
            result = [
                user for user in CoreUser.objects.filter(
                    id__in=user_ids).values(*USER_VALUES)
            ]
        else:
            result = [
                user for user in CoreUser.objects.all().values(*USER_VALUES)
            ]
        return result

    @staticmethod
    def user_delete(request, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        return CoreUser.objects.get(id=user_id).delete()


    @staticmethod
    def user_read(request, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param user_id: string A UUID value identifying the user.
        """
        return CoreUser.objects.filter(id=user_id).values(*USER_VALUES).get()

    @staticmethod
    def user_update(request, body, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param body: dict A dictionary containing the parsed and validated body
        :param user_id: string A UUID value identifying the user.
        """
        instance, created = CoreUser.objects.get_or_create(id=user_id)
        if not created:
            for attr, value in body.items():
                setattr(instance, attr, value)
            instance.save()
        return CoreUser.objects.filter(id=user_id).values(*USER_VALUES).get()
