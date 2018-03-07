"""authentication_service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout, PasswordResetDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView
from django.views.generic import RedirectView, TemplateView

from two_factor.urls import urlpatterns as two_factor_patterns
from two_factor.views import ProfileView

from authentication_service import views

urlpatterns = [
    # Login URLs
    url(r"^login/", views.LoginView.as_view(), name="login"),
    # Override the login URL implicitly defined by Django Admin to redirect
    # to our login view.
    url(
        r"^admin/login/",
        RedirectView.as_view(pattern_name="login", permanent=True,
                             query_string=True)
    ),
    # OOPS URL
    url(
        r"^oops/",
        TemplateView.as_view(
            template_name="authentication_service/demo/oops.html"),
        name="oops"
    ),
    # Reset password URLs
    url(
        r"^reset-password/$",
        views.ResetPasswordView.as_view(),
        name="reset_password"
    ),
    url(
        r"^reset-password/security-questions/$",
        views.ResetPasswordSecurityQuestionsView.as_view(),
        name="reset_password_security_questions"
    ),
    url(
        r"^reset-password/done/$",
        PasswordResetDoneView.as_view(),
        name="password_reset_done"
    ),
    url(
        r"^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm"
    ),
    url(
        r"^reset/complete/$",
        PasswordResetCompleteView.as_view(),
        name="password_reset_complete"
    ),

    url(r"^admin/", admin.site.urls),
    url(r'^admin/defender/', include('defender.urls')),  # defender admin
    url(r"^openid/", include("oidc_provider.urls", namespace="oidc_provider")),
    # Override the login URL implicitly defined by Two Factor Auth to redirect
    # to our login view (which is derived from theirs).
    url(r"^two-factor-auth/account/login/",
        RedirectView.as_view(pattern_name="login", permanent=True,
                             query_string=True)
    ),
    url(r"^two-factor-auth/",
        include(two_factor_patterns, namespace="two_factor_auth")
    ),
    # Registration URLs
    url(
        r"^registration/$",
        views.RegistrationView.as_view(),
        name="registration"
    ),
    url(
        r"^redirect/$",
        views.CookieRedirectView.as_view(),
        name="redirect_view"
    ),
    # Profile Edit URLs
    url(
        r"^profile/edit/",
        login_required(views.EditProfileView.as_view()),
        name="edit_profile"
    ),
    url(
        r"^profile/password/",
        login_required(views.UpdatePasswordView.as_view()),
        name="update_password"
    ),
    url(
        r"^profile/security/",
        login_required(views.UpdateSecurityQuestionsView.as_view()),
        name="update_security_questions"
    ),
    url(
        r"^profile/2fa/",
        login_required(ProfileView.as_view()),
        name="update_2fa"
    ),
    url(
        r"^profile/delete-account/",
        login_required(views.DeleteAccountView.as_view()),
        name="delete_account"
    ),

    url(r"^lockout/$", views.LockoutView.as_view(), name="lockout_view"),
    # Useful url to have, not currently used in any flows.
    url(r"^logout/$",
        logout
    ),

    # API URL's
    url(
        r"api/v1/", include("authentication_service.api.urls"), name="api"
    )
]
