import logging

from django.utils.translation import ugettext as _
from oidc_provider.lib.claims import ScopeClaims


class CustomScopeClaims(ScopeClaims):
    info_roles = (
        _(u"Roles"), _(u"User roles for the requesting site"),
    )

    LOGGER = logging.getLogger(__name__)

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
