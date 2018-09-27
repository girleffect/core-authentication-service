from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from authentication_service import tasks

from project.settings import MediaStorage
from oidc_provider.models import (
    CLIENT_TYPE_CHOICES,
    RESPONSE_TYPE_CHOICES,
    JWT_ALGS
)


def client_logo_path(instance, filename):
    return f"client_logos/user_{instance.requesting_user.id}/{instance.name}_{filename}"


class RequestedClient(models.Model):
    requesting_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Variable names correspond with oidc_provider.models.Client
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    client_type = models.CharField(
        max_length=30,
        choices=CLIENT_TYPE_CHOICES,
        default="confidential",
        verbose_name=_("Client Type"),
        help_text=_(
            "Confidential clients: Are capable of maintaining the confidentiality"
            " of their credentials. "
            "Public clients: are incapable of maintaining the confidentiality."
        )
    )
    response_type = models.CharField(
        max_length=30,
        choices=RESPONSE_TYPE_CHOICES,
        verbose_name=_("Response Type")
    )
    jwt_alg = models.CharField(
        max_length=10,
        choices=JWT_ALGS,
        default="HS256",
        verbose_name=_("JWT Algorithm"),
        help_text=_("Algorithm used to encode ID Tokens.")
    )
    website_url = models.CharField(
        max_length=255, verbose_name=_("Website URL")
    )
    terms_url = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Terms and conditions URL"),
    )
    contact_email = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name=_("Website contact Email")
    )
    # TODO Decide where to store these
    logo = models.ImageField(
        blank=True,
        null=True,
        upload_to=client_logo_path,
        storage=MediaStorage()
    )
    reuse_consent = models.BooleanField(
        default=True,
        verbose_name=_("Reuse Consent?"),
        help_text=_("If enabled, server will save the user consent given to this specific site, "
                    "so that user won\'t be prompted for the same authorization multiple times."))
    redirect_uris = models.TextField(
        verbose_name=_("Redirect URIs"),
        help_text=_("Post login URIs. Please use a comma delimited list."))
    post_logout_redirect_uris = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Post Logout Redirect URIs"),
        help_text=_("Post logout URIs. Please use a comma delimited list."))
    scope = models.TextField(
        blank=True,
        default="",
        verbose_name=_("Scopes"),
        help_text=_("Specifies the authorized scope values for the site."))

def send_request_mail(sender, instance, created, **kwargs):
    if created:
        model = {
            "app_label": instance._meta.app_label,
            "model": instance._meta.model_name,
            "id": instance.id,
            "context_key": "requested_client",
        }
        tasks.send_mail.apply_async(
            kwargs={
                "context": {},
                "mail_type": "request_client_creation",
                "objects_to_fetch": [model]
            }
        )

post_save.connect(send_request_mail, sender=RequestedClient)
