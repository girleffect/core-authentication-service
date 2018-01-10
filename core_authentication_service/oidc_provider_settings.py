import logging

from django.utils.translation import ugettext as _
from oidc_provider.lib.claims import ScopeClaims

USER_MODEL = get_user_model()

'''
# Claims that map to None are known, but have no value we can set.
# Claims for which the resulting function returns None will be automatically
# omitted from the response.
CLAIMS_MAP = {
    "address": None,
    "birthdate": lambda user: user.extra_data.birth_date,
    "email": lambda user: user.email,
    "email_verified": lambda user: user.extra_data.email_verified if
        user.email else None,
    "family_name": lambda user: user.last_name,
    "gender": lambda user: user.extra_data.gender,
    "given_name": lambda user: user.first_name,
    "locale": lambda user: user.extra_data.country.name if
        user.extra_data.country else None,
    # TODO: Using country for locale technically correct. Just using as an
    # example for now.
    "middle_name": lambda user: None,
    "name": lambda user: "{0} {1}".format(user.first_name, user.last_name),
    "nickname": lambda user: user.username,
    "phone_number": lambda user: user.extra_data.msisdn,
    "phone_number_verified": lambda user: user.extra_data.msisdn_verified if
        user.extra_data.msisdn else None,
    "picture": lambda user: user.extra_data.avatar,
    "preferred_username": lambda user: None,
    "profile": lambda user: None,
    "updated_at": lambda user: None,  # TODO: Add to user model
    "website": lambda user: None,
    "zoneinfo": lambda user: None,
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
    LOGGER.debug("Userinfo request for {}: Request: {}".format(user, claims))
    for key in claims.keys():
        if key in CLAIMS_MAP:
            mapfun = CLAIMS_MAP[key]
            if mapfun:
                claims[key] = mapfun(user)
        else:
            LOGGER.error("Unsupported claim '{}' encountered.".format(key))

    LOGGER.debug("Userinfo request for {}: Response: {}".format(user, claims))
    return claims
'''

class CustomScopeClaims(ScopeClaims):
    info_roles = (
        _(u"Roles"), _(u"User roles for the requesting site"),
    )

    def scope_roles(self):
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

        # TODO: Roles need to actually get fetched.
        roles = ["not", "implemented", "yet", "Role G", "Role C"]
        LOGGER.debug("Got roles after possible blocking api call " \
            "to access-control for user: %s on site: %s" % (
            self.user.username,  self.client))
        result = {"roles": roles}

        return result
