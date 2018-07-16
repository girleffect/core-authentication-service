import datetime
import logging

from django.core.exceptions import SuspiciousOperation
from django.urls import reverse
from django.utils import timezone
from oidc_provider.models import Client

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.expressions import RawSQL
from django.shortcuts import get_object_or_404

from authentication_service import tasks
from authentication_service.api.stubs import AbstractStubClass
from authentication_service.exceptions import BadRequestException
from authentication_service.models import CoreUser, Country, Organisation, UserSite
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
ORGANISATION_VALUES = [
    "id", "name", "description", "created_at", "updated_at"
]
USER_VALUES = [
    "id", "username", "first_name", "last_name", "email", "is_active",
    "date_joined", "last_login", "email_verified", "msisdn_verified", "msisdn",
    "gender", "birth_date", "avatar", "country", "created_at", "updated_at",
    "organisation"
]

SUPPORTED_LANGUAGE_CODES = {language[0] for language in settings.LANGUAGES}


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

    # invitation_send -- Synchronisation point for meld
    @staticmethod
    def invitation_send(request, invitation_id, language=None, *args, **kwargs):
        """
        Queue sending of an invitation email.

        This function needs to perform thorough validation of all fields to ensure any errors
        are detected before queuing the task that will send the email asynchronously.

        :param request: An HttpRequest
        :param invitation_id:
        :type invitation_id: string
        :param language: (optional)
        :type language: string
        """
        language = language or "en"  # English is the default language

        if language not in SUPPORTED_LANGUAGE_CODES:
            raise SuspiciousOperation("An unsupported language was specified.")

        invitation = settings.ACCESS_CONTROL_API.invitation_read(invitation_id)

        if invitation is None:
            raise SuspiciousOperation("The specified invitation does not exist.")

        # We need to use timezone.now() instead of datetime.now(), since timezone.now()
        # is timezone aware and is required to be able to compare against invitation.expires_at.
        if invitation.expires_at < timezone.now():
            raise SuspiciousOperation("The specified invitation has expired.")

        # Ensure the invitor exists
        get_object_or_404(CoreUser, id=invitation.invitor_id)
        # Ensure the organisation exists
        get_object_or_404(Organisation, id=invitation.organisation_id)

        registration_url = request.build_absolute_uri(reverse("registration"))

        # CC 2018-07-16: Use sync call until we can figure out the issue with email on prod
        #tasks.send_invitation_email.delay(invitation.to_dict(), registration_url, language)
        tasks.send_invitation_email(invitation.to_dict(), registration_url, language)

        return {}

    # organisation_list -- Synchronisation point for meld
    @staticmethod
    def organisation_list(request, offset=None, limit=None, organisation_ids=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param offset: (optional) An optional query parameter specifying the offset in the result set to start from.
        :type offset: integer
        :param limit: (optional) An optional query parameter to limit the number of results returned.
        :type limit: integer
        :param organisation_ids: (optional) An optional list of organisation ids
        :type organisation_ids: array
        """
        offset = int(offset if offset else settings.DEFAULT_LISTING_OFFSET)
        limit = check_limit(limit)

        organisations = Organisation.objects.order_by("id")

        if organisation_ids:
            organisations = organisations.filter(id__in=organisation_ids)

        organisations = organisations.annotate(
            x_total_count=RawSQL("COUNT(*) OVER ()", [])
        )[offset:offset + limit]
        return (
            [strip_empty_optional_fields(to_dict_with_custom_fields(organisation,
                                                                    ORGANISATION_VALUES))
             for organisation in organisations],
            {
                "X-Total-Count": organisations[0].x_total_count if organisations else 0
            }
        )

    # organisation_create -- Synchronisation point for meld
    @staticmethod
    def organisation_create(request, body, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param body: A dictionary containing the parsed and validated body
        :type body: dict
        """
        organisation = Organisation.objects.create(**body)
        result = to_dict_with_custom_fields(organisation, ORGANISATION_VALUES)
        return strip_empty_optional_fields(result)

    # organisation_delete -- Synchronisation point for meld
    @staticmethod
    def organisation_delete(request, organisation_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param organisation_id: An integer identifying an organisation a user belongs to
        :type organisation_id: integer
        """
        organisation = get_object_or_404(Organisation, id=organisation_id)
        users = CoreUser.objects.filter(organisation=organisation)
        if users:
            LOGGER.warning(
                "Users Linked to organisation {}. Delete Canceled".format(
                    organisation_id
                )
            )
            raise BadRequestException
        else:
            organisation.delete()

    # organisation_read -- Synchronisation point for meld
    @staticmethod
    def organisation_read(request, organisation_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param organisation_id: An integer identifying an organisation a user belongs to
        :type organisation_id: integer
        """
        organisation = get_object_or_404(Organisation, id=organisation_id)
        result = to_dict_with_custom_fields(organisation, ORGANISATION_VALUES)
        return strip_empty_optional_fields(result)

    # organisation_update -- Synchronisation point for meld
    @staticmethod
    def organisation_update(request, body, organisation_id, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param body: A dictionary containing the parsed and validated body
        :type body: dict
        :param organisation_id: An integer identifying an organisation a user belongs to
        :type organisation_id: integer
        """
        organisation = get_object_or_404(Organisation, id=organisation_id)
        for attr, value in body.items():
            try:
                setattr(organisation, attr, value)
            except Exception as e:
                LOGGER.error("Failed to set user attribute %s: %s" % (attr, e))

        organisation.save()
        result = to_dict_with_custom_fields(organisation, ORGANISATION_VALUES)
        return strip_empty_optional_fields(result)

    # user_list -- Synchronisation point for meld
    @staticmethod
    def user_list(request, offset=None, limit=None, birth_date=None, country=None, date_joined=None, email=None, email_verified=None, first_name=None, gender=None, is_active=None, last_login=None, last_name=None, msisdn=None, msisdn_verified=None, nickname=None, organisation_id=None, updated_at=None, username=None, q=None, tfa_enabled=None, has_organisation=None, order_by=None, user_ids=None, site_ids=None, *args, **kwargs):
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
        :param organisation_id: (optional) An optional filter on the organisation id
        :type organisation_id: integer
        :param updated_at: (optional) An optional updated_at range filter
        :type updated_at: string
        :param username: (optional) An optional case insensitive username inner match filter
        :type username: string
        :param q: (optional) An optional case insensitive inner match filter across all searchable text fields
        :type q: string
        :param tfa_enabled: (optional) An optional filter based on whether a user has 2FA enabled or not
        :type tfa_enabled: boolean
        :param has_organisation: (optional) An optional filter based on whether a user belongs to an organisation or not
        :type has_organisation: boolean
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
        if has_organisation is not None:
            check = has_organisation.lower() == "true"
            users = users.filter(
                organisation__isnull=not check
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
        if organisation_id:
            users = users.filter(organisation__id=organisation_id)
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

    @staticmethod
    def purge_expired_invitations(request, cutoff_date=None, *args, **kwargs):
        """
        :param request: An HttpRequest
        :param cutoff_date: An optional cutoff date to purge invites before this date
        :type cutoff_date: date
        """
        if cutoff_date is None:
            cutoff_date = str(datetime.datetime.now().date())
        tasks.purge_expired_invitations.apply_async(
            cutoff_date=cutoff_date
        )
        return
