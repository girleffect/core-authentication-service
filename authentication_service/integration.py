import logging

from oidc_provider.models import Client

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.expressions import RawSQL
from django.shortcuts import get_object_or_404

from authentication_service.api.stubs import AbstractStubClass
from authentication_service.models import CoreUser, Country, OrganisationalUnit, UserSite
from authentication_service.utils import strip_empty_optional_fields, check_limit, \
    to_dict_with_custom_fields, range_filter_parser

LOGGER = logging.getLogger(__name__)

CLIENT_VALUES = [
    "id", "_post_logout_redirect_uris", "_redirect_uris", "client_id",
    "contact_email", "logo", "name", "require_consent", "response_type",
    "reuse_consent", "terms_url", "website_url"
]
COUNTRY_VALUES = [
    "code", "name"
]
ORGANISATIONAL_UNIT_VALUES = [
    "id", "name", "description", "created_at", "updated_at"
]
USER_VALUES = [
    "id", "username", "first_name", "last_name", "email", "is_active",
    "date_joined", "last_login", "email_verified", "msisdn_verified", "msisdn",
    "gender", "birth_date", "avatar", "country", "created_at", "updated_at",
    "organisational_unit"
]


class Implementation(AbstractStubClass):

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
        offset = int(offset if offset else settings.DEFAULT_LISTING_OFFSET)
        limit = check_limit(limit)

        clients = Client.objects.order_by("id")

        if client_ids:
            clients = clients.filter(id__in=client_ids)

        if client_token_id:
            clients = clients.filter(client_id=client_token_id)

        clients = clients.annotate(
            x_total_count=RawSQL("COUNT(*) OVER ()", [])
        )[offset:offset + limit]
        return (
            [strip_empty_optional_fields(to_dict_with_custom_fields(client, CLIENT_VALUES))
             for client in clients],
            {
                "X-Total-Count": clients[0].x_total_count if clients else 0
            }
        )

    # client_read -- Synchronisation point for meld
    @staticmethod
    def client_read(request, client_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param client_id: A string value identifying the client
        :type client_id: string
        """
        client = get_object_or_404(Client, id=client_id)
        result = to_dict_with_custom_fields(client, CLIENT_VALUES)
        return strip_empty_optional_fields(result)

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
        offset = int(offset if offset else settings.DEFAULT_LISTING_OFFSET)
        limit = check_limit(limit)

        countries = Country.objects.order_by("code")

        if country_codes:
            countries = countries.filter(code__in=country_codes)

        countries = countries.annotate(
            x_total_count=RawSQL("COUNT(*) OVER ()", [])
        )[offset:offset + limit]
        return (
            [strip_empty_optional_fields(to_dict_with_custom_fields(country, COUNTRY_VALUES))
             for country in countries],
            {
                "X-Total-Count": countries[0].x_total_count if countries else 0
            }
        )

    # country_read -- Synchronisation point for meld
    @staticmethod
    def country_read(request, country_code, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param country_code: A string value identifying the country
        :type country_code: string
        """
        country = get_object_or_404(Country, code=country_code)
        result = to_dict_with_custom_fields(country, COUNTRY_VALUES)
        return strip_empty_optional_fields(result)

    # organisational_unit_list -- Synchronisation point for meld
    @staticmethod
    def organisational_unit_list(request, offset=None, limit=None, organisational_unit_ids=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param offset: (optional) An optional query parameter specifying the offset in the result set to start from.
        :type offset: integer
        :param limit: (optional) An optional query parameter to limit the number of results returned.
        :type limit: integer
        :param organisational_unit_ids: (optional) An optional list of organisational unit ids
        :type organisational_unit_ids: array
        """
        offset = int(offset if offset else settings.DEFAULT_LISTING_OFFSET)
        limit = check_limit(limit)

        organisational_units = OrganisationalUnit.objects.order_by("id")

        if organisational_unit_ids:
            organisational_units = organisational_units.filter(id__in=organisational_unit_ids)

        organisational_units = organisational_units.annotate(
            x_total_count=RawSQL("COUNT(*) OVER ()", [])
        )[offset:offset + limit]
        return (
            [strip_empty_optional_fields(to_dict_with_custom_fields(organisational_unit,
                                                                    ORGANISATIONAL_UNIT_VALUES))
             for organisational_unit in organisational_units],
            {
                "X-Total-Count": organisational_units[0].x_total_count if organisational_units else 0
            }
        )

    # organisational_unit_read -- Synchronisation point for meld
    @staticmethod
    def organisational_unit_read(request, organisational_unit_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param organisational_unit_id: An integer identifying an organisational unit
        :type organisational_unit_id: integer
        """
        organisational_unit = get_object_or_404(OrganisationalUnit, id=organisational_unit_id)
        result = to_dict_with_custom_fields(organisational_unit, ORGANISATIONAL_UNIT_VALUES)
        return strip_empty_optional_fields(result)

    # user_list -- Synchronisation point for meld
    @staticmethod
    def user_list(request, offset=None, limit=None, birth_date=None, country=None, date_joined=None, email=None, email_verified=None, first_name=None, gender=None, is_active=None, last_login=None, last_name=None, msisdn=None, msisdn_verified=None, nickname=None, organisational_unit_id=None, updated_at=None, username=None, q=None, tfa_enabled=None, has_organisational_unit=None, order_by=None, user_ids=None, site_ids=None, *args, **kwargs):
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
        :param organisational_unit_id: (optional) An optional filter on the organisational unit id
        :type organisational_unit_id: integer
        :param updated_at: (optional) An optional updated_at range filter
        :type updated_at: string
        :param username: (optional) An optional case insensitive username inner match filter
        :type username: string
        :param q: (optional) An optional case insensitive inner match filter across all searchable text fields
        :type q: string
        :param tfa_enabled: (optional) An optional filter based on whether a user has 2FA enabled or not
        :type tfa_enabled: boolean
        :param has_organisational_unit: (optional) An optional filter based on whether a user has an organisational unit or not
        :type has_organisational_unit: boolean
        :param order_by: (optional) Fields and directions to order by, e.g. "-created_at,username". Add "-" in front of a field name to indicate descending order.
        :type order_by: array
        :param user_ids: (optional) An optional list of user ids
        :type user_ids: array
        :param site_ids: (optional) An optional list of site ids
        :type site_ids: array
        """
        offset = int(offset if offset else settings.DEFAULT_LISTING_OFFSET)
        limit = check_limit(limit)

        order_by = order_by or ["id"]
        users = get_user_model().objects.order_by(*order_by)

        # Bools
        if tfa_enabled is not None:
            check = tfa_enabled.lower() == "true"
            users = users.filter(
                totpdevice__isnull=not check
            )
        if has_organisational_unit is not None:
            check = has_organisational_unit.lower() == "true"
            users = users.filter(
                organisational_unit__isnull=not check
            )
        if email_verified is not None:
            users = users.filter(
                email_verified=email_verified.lower() == "true"
            )
        if is_active is not None:
            users = users.filter(
                is_active=is_active.lower() == "true"
            )
        if msisdn_verified is not None:
            users = users.filter(
                msisdn_verified=msisdn_verified.lower() == "true"
            )

        # Dates
        if birth_date:
            ranges = range_filter_parser(birth_date)
            users = users.filter(**{"birth_date__%s" % k: v for k, v in ranges.items()})
        if date_joined:
            ranges = range_filter_parser(date_joined)
            users = users.filter(**{"date_joined__date__%s" % k: v for k, v in ranges.items()})
        if last_login:
            ranges = range_filter_parser(last_login)
            users = users.filter(**{"last_login__date__%s" % k: v for k, v in ranges.items()})
        if updated_at:
            ranges = range_filter_parser(updated_at)
            users = users.filter(**{"updated_at__date__%s" % k: v for k, v in ranges.items()})

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
        if site_ids:
            # In order for the count to be correct, we cannot join with the UserSite table and
            # need to use a subquery.
            site_user_ids = UserSite.objects.distinct().filter(site_id__in=site_ids).values(
                "user_id")
            users = users.filter(id__in=site_user_ids)

        # Add count
        users = users.annotate(
            x_total_count=RawSQL("COUNT(*) OVER ()", [])
        )
        # Perform the query and get the correct slice
        users = users[offset:offset + limit]
        return (
            [strip_empty_optional_fields(to_dict_with_custom_fields(user, USER_VALUES))
             for user in users],
            {
                "X-Total-Count": users[0].x_total_count if users else 0
            }
        )

    # user_delete -- Synchronisation point for meld
    @staticmethod
    def user_delete(request, user_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param user_id: A UUID value identifying the user.
        :type user_id: string
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
        :param user_id: A UUID value identifying the user.
        :type user_id: string
        """
        user = get_object_or_404(CoreUser, id=user_id)
        result = to_dict_with_custom_fields(user, USER_VALUES)
        return strip_empty_optional_fields(result)

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
        instance = get_object_or_404(CoreUser, id=user_id)
        for attr, value in body.items():
            try:
                setattr(instance, attr, value)
            except Exception as e:
                LOGGER.error("Failed to set user attribute %s: %s" % (attr, e))

        instance.save()
        result = to_dict_with_custom_fields(instance, USER_VALUES)
        return strip_empty_optional_fields(result)
