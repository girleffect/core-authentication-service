import logging

from oidc_provider.models import Client

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.expressions import RawSQL
from django.forms import model_to_dict
from django.http import Http404
from django.shortcuts import get_object_or_404

from authentication_service.api.stubs import AbstractStubClass
from authentication_service.models import CoreUser
from authentication_service.utils import (strip_empty_optional_fields,
    check_limit, to_dict_with_custom_fields, range_filter_parser)

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
    def user_list(request, offset=None, limit=None, birth_date=None, country=None, date_joined=None,
                  email=None, email_verified=None, first_name=None, gender=None, is_active=None,
                  last_login=None, last_name=None, msisdn=None, msisdn_verified=None, nickname=None,
                  organisational_unit_id=None, updated_at=None, username=None, q=None,
                  tfa_enabled=None, has_organisational_unit=None, order_by=None, user_ids=None,
                  *args, **kwargs):
        """
        :param request: An HttpRequest
        """
        offset = int(offset if offset else settings.DEFAULT_LISTING_OFFSET)
        limit = check_limit(limit)

        order_by = order_by or ["id"]
        users = get_user_model().objects.values(
            *USER_VALUES).order_by(*order_by)

        # Bools
        if tfa_enabled is not None:
            check = True if tfa_enabled.lower() == "true" else False
            users = users.filter(
                totpdevice__isnull=not check
            )
        if has_organisational_unit is not None:
            check = True if has_organisational_unit.lower() == "true" else False
            users = users.filter(
                organisational_unit__isnull=not check
            )
        if email_verified is not None:
            users = users.filter(
                email_verified=True if email_verified.lower() == "true"
                else False
            )
        if is_active is not None:
            users = users.filter(
                is_active=True if is_active.lower() == "true"
                else False
            )
        if msisdn_verified is not None:
            users = users.filter(
                msisdn_verified=True if msisdn_verified.lower() == "true"
                else False
            )

        # Dates
        if birth_date:
            ranges = range_filter_parser(birth_date)
            users = users.filter(**{"birth_date__%s" % ranges[0]:ranges[1]})
        if date_joined:
            ranges = range_filter_parser(date_joined)
            users = users.filter(**{"date_joined__%s" % ranges[0]:ranges[1]})
        if last_login:
            ranges = range_filter_parser(last_login)
            users = users.filter(**{"last_login__%s" % ranges[0]:ranges[1]})
        if updated_at:
            ranges = range_filter_parser(updated_at)
            users = users.filter(**{"updated_at__%s" % ranges[0]:ranges[1]})

        # Partial matches
        if email:
            users = users.filter(email__ilike=email)
        if first_name:
            users = users.filter(first_name__ilike=first_name)
        if username:
            users = users.filter(username__ilike=username)
        if msisdn:
            users = users.filter(msisdn__ilike=msisdn)
        if last_name:
            users = users.filter(last_name__ilike=last_name)
        if nickname:
            users = users.filter(nickname__ilike=nickname)
        if q:
            users = users.filter(q__ilike=q)

        # Other filters
        if country:
            users = users.filter(country__code=country)
        if user_ids:
            users = users.filter(id__in=user_ids)
        if gender:
            users = users.filter(gender=gender)
        if organisational_unit_id:
            users = users.filter(organisational_unit__id=organisational_unit_id)

        # Count
        users = users.annotate(
            x_total_count=RawSQL("COUNT(*) OVER ()", [])
        )[offset:offset + limit]
        return (
            [strip_empty_optional_fields(user) for user in users],
            {
                "X-Total-Count": users[0][
                    "x_total_count"] if len(users) > 0 else 0
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
