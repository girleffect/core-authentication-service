import logging

from django.utils.translation import ugettext as _
from django.contrib.auth import get_user_model

from oidc_provider.lib.claims import ScopeClaims


USER_MODEL = get_user_model()

# Claims that map to None are known, but have no value we can set.
# Claims for which the resulting function returns None will be automatically
# omitted from the response.
CLAIMS_MAP = {
    "name": lambda user: "%s %s" % (user.first_name, user.last_name) \
        if user.first_name and user.last_name else None,
    "given_name": lambda user: user.first_name if user.first_name else None,
    "family_name": lambda user: user.last_name if user.last_name else None,
    "middle_name": None,
    "nickname": lambda user: user.nickname if user.nickname else user.username,
    "profile": lambda user: None,
    "preferred_username": lambda user: user.nickname or user.username,
    "picture": lambda user: user.avatar if user.avatar else None,
    "website": lambda user: None,
    "gender": lambda user: user.gender if user.gender else None,
    "birthdate": lambda user: user.birth_date if user.birth_date else None,
    "zoneinfo": lambda user: None,
    "locale": lambda user: user.country.code if
        user.country else None,
    "updated_at": lambda user: user.updated_at,
    "email": lambda user: user.email if user.email else None,
    "email_verified": lambda user: user.email_verified if
        user.email else None,
    "phone_number": lambda user: user.msisdn if user.msisdn else None,
    "phone_number_verified": lambda user: user.msisdn_verified if
        user.msisdn else None,
    "address": None,
}

LOGGER = logging.getLogger(__name__)


def userinfo(claims: dict, user: USER_MODEL) -> dict:
    """
    This function handles the standard claims defined for OpenID Connect.
    IMPORTANT: No keys may be removed or added to the claims dictionary.
    :param claims: A dictionary with claims as keys
    :param user: The user for which the information is claimed
    :return: The claims dictionary populated with values
    """
    LOGGER.debug("User info request for {}: Claims={}".format(user, claims))
    for key in claims:
        if key in CLAIMS_MAP:
            mapfun = CLAIMS_MAP[key]
            if mapfun:
                claims[key] = mapfun(user)
        else:
            LOGGER.error("Unsupported claim '{}' encountered.".format(key))

    return claims


class CustomScopeClaims(ScopeClaims):
    """
    A class facilitating custom scopes and claims. For more information, see
    http://django-oidc-provider.readthedocs.io/en/latest/sections/scopesclaims.html#how-to-add-custom-scopes-and-claims
    """

    info_site = (
        _(u"Site"), _(u"Data for the requesting site"),
    )

    info_roles = (
        _(u"Roles"), _(u"Roles for the requesting site"),
    )

    def scope_site(self) -> dict:
        """
        The following attributes are available when constructing custom scopes:
        * self.user: The Django user instance.
        * self.userinfo: The dict returned by the OIDC_USERINFO function.
        * self.scopes: A list of scopes requested.
        * self.client: The Client requesting this claim.
        :return: A dictionary containing the claims for the custom Site scope
        """
        LOGGER.debug("Looking up site {} data for user {}".format(
            self.client.client_id, self.user))
        # TODO:
        # 1. Use the client id to query the Access Control component for the site id linked to it
        #  this client.
        # 2. Use the site id and user id to query the User Data Store component for the
        #  site-specific data for the user.
        result = {
            "site": {
                "id": self.client.client_id,
                "mocked": True,
                "status": "This is demo data"
            }
        }

        return result

    def scope_roles(self) -> dict:
        """
        The following attributes are available when constructing custom scopes:
        * self.user: The Django user instance.
        * self.userinfo: The dict returned by the OIDC_USERINFO function.
        * self.scopes: A list of scopes requested.
        * self.client: The Client requesting this claim.
        :return: A dictionary containing the user roles as a list
        """
        LOGGER.debug("Requesting roles for user: %s/%s, on site: %s" % (
            self.user.username, self.user.id, self.client))

        # TODO: Roles need to actually get fetched. We fake it for now.
        # Keep imports here as well, nuke everything when it gets replaced.
        import json
        with open("authentication_service/demo/roles.json") as f:
            data = json.load(f)
        roles = data[self.client.client_id].get(str(self.user.id), ["NoRoles"])
        result = {"roles": roles}

        return result
