from urllib.parse import \
    urlsplit, parse_qs, urlunsplit, urlencode, urlparse

import datetime
import pkg_resources
import socket
import urllib

import prometheus_client
from defender.decorators import watch_login
from defender.utils import is_user_already_locked, lockout_response
from formtools.wizard.views import NamedUrlSessionWizardView

from oidc_provider.models import Client
from oidc_provider.views import EndSessionView
from oidc_provider import settings as oidc_settings
from oidc_provider.lib.utils.token import client_id_from_id_token

from two_factor.forms import AuthenticationTokenForm
from two_factor.forms import BackupTokenForm
from two_factor.utils import default_device
from two_factor.views import core

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.signals import user_logged_out
from django.contrib.auth import login, authenticate, hashers
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
    LogoutView
)
from django.contrib.auth import get_user_model
from django.core import signing
from django.core.exceptions import ValidationError
from django.core.files.storage import DefaultStorage
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import connection
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import LANGUAGE_SESSION_KEY

# NOTE: Can be refactored, both redirect import perform more or less the same.
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.views.generic import View, TemplateView
from django.views.decorators.cache import never_cache
from django.views.generic.edit import UpdateView, FormView

from authentication_service import api_helpers
from authentication_service.forms import LoginForm
from authentication_service.decorators import generic_deprecation
from authentication_service import forms, models, tasks, constants, utils
from authentication_service.user_migration.models import TemporaryMigrationUserStore


CLIENT_URI_SESSION_KEY = constants.SessionKeys.CLIENT_URI
USER_MODEL = get_user_model()


class AnonUserRequiredMixin(object):

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('edit_profile')
        return super(AnonUserRequiredMixin, self).dispatch(request, *args, **kwargs)


class LanguageMixin:
    """This mixin sets an instance variable called self.language, value is
    passed in via url or determined by django language middleware
    """

    def dispatch(self, *args, **kwargs):
        self.language = self.request.GET.get("language") \
            if self.request.GET.get("language") else self.request.LANGUAGE_CODE
        return super(LanguageMixin, self).dispatch(*args, **kwargs)


class LockoutView(TemplateView):
    """
    A view used by Defender to inform the user that they have exceeded the
    threshold for allowed login failures or password reset attempts.
    """
    template_name = "authentication_service/lockout.html"

    def get_context_data(self, *args, **kwargs):
        ct = super(LockoutView, self).get_context_data(*args, **kwargs)
        ct["referrer"] = self.request.META.get("HTTP_REFERER")
        ct["failure_limit"] = settings.DEFENDER_LOGIN_FAILURE_LIMIT
        ct["cooloff_time_minutes"] = int(settings.DEFENDER_COOLOFF_TIME / 60)
        return ct


class LoginView(AnonUserRequiredMixin, core.LoginView):
    """This view simply extends the LoginView from two_factor.views.core. We
    only override the template and the done step, which we use to login
    superusers.
    """
    template_name = "authentication_service/login.html"

    form_list = (
        ("auth", LoginForm),
        ("token", AuthenticationTokenForm),
        ("backup", BackupTokenForm),
    )

    @generic_deprecation(
        "authentication_service.views.LoginView: def post(); makes use of"
        " models and urls found in 'authentication_service.user_migration'."
        " The app is temporary and will be removed."
    )
    def post(self, *args, **kwargs):
        # Short circuit normal login flow as needed to migrate old existing
        # users.

        # Super can not be called first. The temporary user objects will break
        # functionality in the base view. Only attempt on the first step.
        if self.get_step_index() == 0:
            form = self.get_form(
                data=self.request.POST, files=self.request.FILES
            )

            # Is valid triggers authentication.
            if not form.is_valid():
                form_user = form.get_user()

                # Only to be triggered during oidc login, next containing
                # client_id is expected
                next_query = self.request.GET.get("next")
                if next_query:
                    next_query_args = parse_qs(urlparse(next_query).query)

                    # Query values are in list form. Only grab the first value
                    # from the list.
                    client_id = next_query_args.get("client_id", [None])[0]

                    # Only do these checks if no user was authenticated and
                    # client_id is present. Also need to ensure form values are
                    # present.
                    username = form.cleaned_data.get("username", None)
                    password = form.cleaned_data.get("password", None)
                    if form_user is None and client_id and username and password:
                        try:
                            user = TemporaryMigrationUserStore.objects.get(
                                username=username, client_id=client_id
                            )

                            token = signing.dumps(
                                user.id, salt="ge-migration-user-registration"
                            )

                            # If the temp user password matches, redirect to
                            # migration wizard.
                            if user.check_password(password):
                                querystring = urllib.parse.quote_plus(
                                    self.request.GET.get("next", "")
                                )
                                url = reverse(
                                    "user_migration:migrate_user", kwargs={
                                        "token": token
                                    }
                                )
                                return redirect(
                                    f"{url}?persist_query={querystring}"
                                )
                        except TemporaryMigrationUserStore.DoesNotExist:
                            # Let login fail as usual
                            pass
        return super(LoginView, self).post(*args, **kwargs)


class AuthServiceLogout(LogoutView):
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            user = None
        user_logged_out.send(sender=user.__class__, request=request, user=user)

        # remember language choice saved to session
        language = request.session.get(LANGUAGE_SESSION_KEY)
        theme = utils.get_session_data(request, constants.SessionKeys.THEME)

        request.session.flush()
        if theme:
            utils.update_session_data(
                request, constants.SessionKeys.THEME, theme)

        if language:
            request.session[LANGUAGE_SESSION_KEY] = language

        request.user = AnonymousUser()
        next_page = self.get_next_page()
        if next_page:
            # Redirect to this page until the session has been cleared.
            return HttpResponseRedirect(next_page)
        return super(LogoutView, self).dispatch(request, *args, **kwargs)


class AuthServiceEndService(LoginRequiredMixin, EndSessionView):
    def get(self, request, *args, **kwargs):
        id_token_hint = request.GET.get('id_token_hint', '')
        post_logout_redirect_uri = request.GET.get('post_logout_redirect_uri', '')
        state = request.GET.get('state', '')
        client = None

        next_page = oidc_settings.get('OIDC_LOGIN_URL')
        after_end_session_hook = oidc_settings.get(
            'OIDC_AFTER_END_SESSION_HOOK', import_str=True)

        if id_token_hint:
            client_id = client_id_from_id_token(id_token_hint)
            try:
                client = Client.objects.get(client_id=client_id)
                if post_logout_redirect_uri in client.post_logout_redirect_uris:
                    if state:
                        uri = urlsplit(post_logout_redirect_uri)
                        query_params = parse_qs(uri.query)
                        query_params['state'] = state
                        uri = uri._replace(query=urlencode(query_params, doseq=True))
                        next_page = urlunsplit(uri)
                    else:
                        next_page = post_logout_redirect_uri
            except Client.DoesNotExist:
                pass

        after_end_session_hook(
            request=request,
            id_token=id_token_hint,
            post_logout_redirect_uri=post_logout_redirect_uri,
            state=state,
            client=client,
            next_page=next_page
        )
        return AuthServiceLogout.as_view(next_page=next_page)(request)


# Protect the login view using Defender. Defender provides a method decorator
# which we have to tweak to apply to the dispatch method of a view.
# This is based on their own implementation of their middleware class:
# https://github.com/kencochrane/django-defender/blob/master/defender/middleware.py#L24-L27
defender_decorator = watch_login()
watch_login_method = method_decorator(defender_decorator)
LoginView.dispatch = watch_login_method(LoginView.dispatch)

registration_forms = (
    ("userdata", forms.RegistrationForm),
    ("securityquestions", forms.SecurityQuestionFormSet),
)


def show_security_questions(wizard):
    cleaned_data = wizard.get_cleaned_data_for_step(
        "userdata") or {"email": None}
    return cleaned_data["email"] is None


class RegistrationWizard(AnonUserRequiredMixin, LanguageMixin, NamedUrlSessionWizardView):
    form_list = registration_forms
    condition_dict = {"securityquestions": show_security_questions}
    template_name = "authentication_service/registration.html"
    file_storage = DefaultStorage()

    # Needed to stop a NoneType error from triggering in django internals. The
    # formset does not require a queryset.
    instance_dict = {
        "securityquestions": models.UserSecurityQuestion.objects.none()
    }
    security = None

    def _url_signature_error(self):
        return render(
            self.request,
            "authentication_service/message.html",
            context={
                "page_meta_title": _("Registration invitation error"),
                "page_title": _("Registration invitation error"),
                "page_message": _(
                    "The invitation is incorrect or the URL" \
                    " has been tampered with."
                ),
            }
        )

    def _render_expired_invitation_page(self, inviter):
        return render(
            self.request,
            "authentication_service/message.html",
            context={
                "page_meta_title": _("Registration invitation expired"),
                "page_title": _("Registration invitation expired"),
                "page_message": _(
                    "The invitation has expired."\
                    f" Please contact {inviter.first_name} {inviter.last_name}" \
                    f" at {inviter.email}"
                ),
            }
        )

    @cached_property
    def inviter(self):
        """
        Only called during two errors, no need to do a lookup if the view
        didn't error.
        """
        admin_id = self.storage.extra_data.get("invitation_data", {}).get("invitor_id")
        try:
            return USER_MODEL.objects.get(
                id=admin_id
            )
        except USER_MODEL.DoesNotExist:
            raise Http404(
                f"Admin tied to invite id {admin_id} does not exist."
            )

    def dispatch(self, request, *args, **kwargs):
        dispatch = super(RegistrationWizard, self).dispatch(request, *args, **kwargs)

        # Validate invitation and get data.
        invitation = self.request.GET.get("invitation")
        api_invitation = None
        if invitation:
            try:
                invitation_data = signing.loads(
                    invitation,
                    salt="invitation",
                )
            except signing.BadSignature:
                return self._url_signature_error()

            # ID is required for the api call
            if not invitation_data.get("invitation_id"):
                return self._url_signature_error()
            api_invitation = api_helpers.get_invitation_data(
                invitation_data.pop("invitation_id")
            )

            # Do some validation with the invitation data
            if api_invitation.get("error") is True:
                return self._url_signature_error()
            # Prevents needing to manipulate data before being saved to
            # session storage.
            del api_invitation["created_at"]
            del api_invitation["updated_at"]
            expires_at = api_invitation.pop("expires_at")

            # Storage value needed for the inviter property and organisation
            self.storage.extra_data["invitation_data"] = api_invitation
            self.storage.extra_data["invitation_setup"] = invitation_data

            if expires_at < timezone.now():
                return self._render_expired_invitation_page(self.inviter)

            # Check if org exists
            try:
                self.organisation = models.Organisation.objects.get(
                    id=api_invitation["organisation_id"]
                )
            except models.Organisation.DoesNotExist:
                raise Http404(
                    f"Organisation you have been invited for does not exist."
                )

        return dispatch

    def get_form_initial(self, step):
        initial = super(RegistrationWizard, self).get_form_kwargs()

        invitation = self.storage.extra_data.get("invitation_data")
        if step == "userdata" and invitation:
            initial = {
                "first_name": invitation.get("first_name"),
                "last_name": invitation.get("last_name"),
                "email": invitation.get("email"),
            }
        # Formsets take a list of dictionaries for initial data.
        if step == "securityquestions":
            initial = [
                {"question": q_id}
                for q_id in self.storage.extra_data.get("question_ids", [])
            ]
        return initial

    def get_form_kwargs(self, step=None):
        custom_kwargs = {
            "security": self.request.GET.get("security"),
            "required": self.request.GET.getlist("requires"),
            "hidden": self.request.GET.getlist("hide"),
            "question_ids": self.request.GET.getlist("question_ids", []),
        }

        custom_kwargs.update(
            self.storage.extra_data.get("invitation_setup", {})
        )

        # Need to set these values once, but guard against clearing them.
        for key, value in custom_kwargs.items():
            if value:
                self.storage.extra_data[key] = value

        kwargs = super(RegistrationWizard, self).get_form_kwargs()
        if step == "userdata":
            security = self.storage.extra_data.get("security")
            hidden = self.storage.extra_data.get("hidden")
            required = self.storage.extra_data.get("required")
            kwargs["terms_url"] = utils.get_session_data(
                self.request,
                constants.SessionKeys.CLIENT_TERMS
            )
            if security:
                kwargs["security"] = security.lower()
            if required:
                kwargs["required"] = required
            if hidden:
                kwargs["hidden"] = hidden

            # Organisation id, used to do a lot of extra work on the form if
            # supplied.
            kwargs["organisation_id"] = self.storage.extra_data.get(
                "invitation_data", {}).get("organisation_id")

        if step == "securityquestions":
            kwargs = {
                "language": self.language,
                "step_email": self.get_cleaned_data_for_step(
                    "userdata"
                ).get("email")
            }
        return kwargs

    def done(self, form_list, **kwargs):
        formset = kwargs["form_dict"].get("securityquestions")

        # Once form is saved the data gets removed from the
        # get_all_cleaned_data, store the values before saving. The values are
        # needed to login user.
        username = self.get_all_cleaned_data()["username"]
        pwd = self.get_all_cleaned_data()["password1"]

        # Save user model
        user = kwargs["form_dict"]["userdata"].save()

        # Do some work and assign questions to the user.
        for form in getattr(formset, "forms", []):
            # Trust that form did its work. In the event that not all questions
            # were answered, save what can be saved.
            if form.cleaned_data.get(
                    "answer", None) and form.cleaned_data.get(
                    "question", None):

                # All fields on model are required, as such it requires the
                # full set of data.
                data = form.cleaned_data
                data["user_id"] = user.id
                data["language_code"] = self.language
                models.UserSecurityQuestion.objects.create(**data)
        invitation = self.storage.extra_data.get("invitation_data")
        if invitation:
            response = api_helpers.invitation_redeem(invitation["id"], user.id)
            if response.get("error"):
                inviter = self.inviter
                return render(
                    self.request,
                    "authentication_service/message.html",
                    context={
                        "page_meta_title": _("Registration invite error"),
                        "page_title": _("Registration invite error"),
                        "page_message": _(
                            "Oops. You have successfully registered for a" \
                            " Girl Effect account. Unfortunately something" \
                            " went wrong while redeeming the invitation." \
                            f" Please contact {inviter.first_name}" \
                            f"{inviter.last_name} at {inviter.email}"
                        ),
                    }
                )

        # GE-1065 requires ALL users to be logged in
        self.new_user = authenticate(username=username,
                                password=pwd)
        return self.get_success_response()

    def render_done(self, form, **kwargs):
        # Validate all forms again. If valid calls done() and clears storage.
        response = super(RegistrationWizard, self).render_done(form, **kwargs)

        # Ensure new user is present as set in done, if it is log new user in.
        # Clearing old session in the progress.
        if hasattr(self, "new_user"):
            login(self.request, self.new_user)
        return response

    def get_success_response(self):
        key = CLIENT_URI_SESSION_KEY
        invitation = self.storage.extra_data.get("invitation_setup")
        if invitation and "redirect_url" in invitation:
            # If a redirect URL was specified in the invitation, it takes precedence.
            invitation_redirect_url = invitation["redirect_url"]
            uri = None
        else:
            invitation_redirect_url = None
            uri = utils.get_session_data(self.request, key)

        ## GE-1117: Disabled
        #if hasattr(
        #        self, "security"
        #) and self.security == "high" or self.request.GET.get(
        #        "show2fa") == "true":
        #    return reverse("two_factor_auth:setup")
        if uri:
            return redirect(uri)

        context = {
            "page_meta_title": _("Registration success"),
            "page_title": _("Registration success"),
            "page_message": _("Congratulations, you have successfully registered for a Girl Effect "
                              "account."),
        }
        if invitation_redirect_url:
            context["redirect_url"] = invitation_redirect_url

        return render(
            self.request,
            "authentication_service/message.html",
            context=context
        )


class SessionRedirectView(View):
    """
    Simple view that redirects to a URL stored on the session, if available.
    If none was set, it will redirect to a default page.
    """
    def dispatch(self, request, *args, **kwargs):
        # No need for super, this view should at this stage not need any of its
        # http method functions.
        url = utils.get_session_data(request, CLIENT_URI_SESSION_KEY)

        if url:
            return HttpResponseRedirect(url)

        # Default fallback if no url was set.
        return HttpResponseRedirect(settings.LOGIN_URL)


class EditProfileView(LanguageMixin, UpdateView):
    template_name = "authentication_service/profile/edit_profile.html"
    form_class = forms.EditProfileForm

    def get_context_data(self, **kwargs):
        context = super(EditProfileView, self).get_context_data(**kwargs)

        # Check if user has 2fa enabled
        if default_device(self.request.user):
            context["2fa_enabled"] = True
        return context

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        key = CLIENT_URI_SESSION_KEY
        uri = utils.get_session_data(self.request, key)
        if uri:
            return uri
        messages.success(
            self.request,
            _("Successfully updated profile.")
        )
        return reverse("edit_profile")


class UpdatePasswordView(LanguageMixin, PasswordChangeView):
    template_name = "authentication_service/profile/update_password.html"
    form_class = forms.PasswordChangeForm
    success_url = reverse_lazy("edit_profile")

    def form_valid(self, form):
        if form.is_valid:
            messages.success(
                self.request,
                _("Successfully updated password.")
            )
        return super(UpdatePasswordView, self).form_valid(form)


class UpdateSecurityQuestionsView(LanguageMixin, TemplateView):
    template_name = \
        "authentication_service/profile/update_security_questions.html"
    success_url = reverse_lazy("edit_profile")

    @property
    def get_formset(self):
        queryset = models.UserSecurityQuestion.objects.filter(
            user=self.request.user
        )
        formset = forms.UpdateSecurityQuestionFormSet(
            language=self.language, queryset=queryset
        )
        if self.request.POST:
            formset = forms.UpdateSecurityQuestionFormSet(
                data=self.request.POST,
                language=self.language,
                queryset=queryset
            )
        return formset

    def render(self, request, formset):
        return render(
            request,
            self.get_template_names(),
            context=self.get_context_data(formset=formset)
        )

    def get(self, request, *args, **kwargs):
        formset = self.get_formset
        return self.render(request, formset)

    def get_context_data(self, *args, **kwargs):
        ct = {
            "question_formset": kwargs["question_formset"]
            if kwargs.get("question_formset") else self.get_formset
        }

        # Either a new formset instance or an existing one is passed to the
        # formset class.
        if kwargs.get("question_formset"):
            ct["question_formset"] = kwargs["question_formset"]
        else:
            ct["question_formset"] = self.get_formset
        return ct

    def post(self, request, *args, **kwargs):
        formset = self.get_formset
        if formset.is_valid():
            formset.save()
            return HttpResponseRedirect(self.success_url)
        else:
            return self.render(request, formset)


class DeleteAccountView(FormView):
    template_name = "authentication_service/profile/delete_account.html"
    form_class = forms.DeleteAccountForm
    success_url = reverse_lazy("edit_profile")

    def get_context_data(self, *args, **kwargs):
        ct = super(DeleteAccountView, self).get_context_data(*args, **kwargs)
        ct["confirm"] = False
        if kwargs.get("confirm"):
            ct["confirm"] = True
        return ct

    def form_valid(self, form):
        if "confirmed_deletion" not in self.request.POST:
            return self.render_to_response(self.get_context_data(
                form=form, confirm=True
            ))
        else:
            user = self.request.user
            user = {
                "app_label": user._meta.app_label,
                "model": user._meta.model_name,
                "id": user.id,
                "context_key": "user",
            }
            tasks.send_mail.apply_async(
                kwargs={
                    "context": {"reason": form.cleaned_data["reason"]},
                    "mail_type": "delete_account",
                    "objects_to_fetch": [user]
                }
            )
            messages.success(self.request, _("Successfully requested account deletion."))
            return super(DeleteAccountView, self).form_valid(form)


class ResetPasswordView(AnonUserRequiredMixin, PasswordResetView):
    """This view allows the user to enter either their username or their email
    address in order for us to identify them. After we have identified the user
    we check what method to user to help them reset their password. If the user
    has an email address, we send them a reset link. If they have security
    questions, we take them to the ResetPasswordSecurityQuestionsView to enter
    their answers.
    """
    template_name = "authentication_service/reset_password/reset_password.html"
    form_class = forms.ResetPasswordForm
    success_url = reverse_lazy("password_reset_done")
    #email_template_name = "reset_password/password_reset_email.html"

    def looks_like_email(self, identifier):
        return "@" in identifier

    def form_valid(self, form):
        identifier = form.cleaned_data["email"]

        # Identify user
        user = None
        if self.looks_like_email(identifier):
            user = models.CoreUser.objects.filter(email=identifier).first()

        if not user:
            user = models.CoreUser.objects.filter(
                username=identifier).first()

        # Check reset method
        if user:
            # Check if this user has been locked out
            if is_user_already_locked(user.username):
                return lockout_response(self.request)

            # Store the id of the user that we found in our search
            self.request.session["lookup_user_id"] = str(user.id)

            # Check if user has email or security questions.
            if user.email:
                form.cleaned_data["email"] = user.email
            elif user.has_security_questions:
                self.success_url = reverse("reset_password_security_questions")
            else:  # This should never be the case.
                print("User %s cannot reset their password." % identifier)
        elif not user:
            client_id = utils.get_session_data(
                self.request, constants.SessionKeys.CLIENT_ID
            )
            if client_id:
                # Let it raise a DoesNotExist error. Something is very wrong
                # if that is the case.
                client = Client.objects.get(id=client_id)
                try:
                    user = TemporaryMigrationUserStore.objects.get(
                        username=identifier, client_id=client.client_id
                    )
                    if not user.answer_one and not user.answer_two:
                        # If the user does not have a single answer, add a
                        # message and redirect back to the current view.
                        messages.warning(
                            self.request,
                            _("We are sorry, your account can not perform this action")
                        )

                        # Redirect to current url with entire querystring
                        # present.
                        return redirect(self.request.get_full_path())
                    token = signing.dumps(
                        user.id, salt="ge-migration-user-pwd-reset"
                    )

                    # TODO: Client will raise eventually, after pwd reset there
                    # is no way to enter back into login flow. Outside the
                    # scope of GE-1085 to add. That is the current expected
                    # behaviour.
                    #querystring =  urllib.parse.quote_plus(
                    #    self.request.GET.get("persist_query", "")
                    #)
                    url = reverse(
                        "user_migration:question_gate", kwargs={
                            "token": token
                        }
                    )
                    return redirect(url)
                except TemporaryMigrationUserStore.DoesNotExist:
                    pass

            return HttpResponseRedirect(reverse("password_reset_done"))
        return super(ResetPasswordView, self).form_valid(form)


class ResetPasswordSecurityQuestionsView(FormView):
    template_name = \
        "authentication_service/reset_password/security_questions.html"
    form_class = forms.ResetPasswordSecurityQuestionsForm

    def get_form_kwargs(self):
        kwargs = super(
            ResetPasswordSecurityQuestionsView, self).get_form_kwargs()
        kwargs["questions"] = \
            models.UserSecurityQuestion.objects.filter(
                user__id=self.request.session["lookup_user_id"])
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(ResetPasswordSecurityQuestionsView, self).get_context_data(**kwargs)
        context["username"] = models.CoreUser.objects.get(
            id=self.request.session["lookup_user_id"]).username
        return context

    def form_valid(self, form):
        for question in form.questions:
            if not hashers.check_password(
                    form.cleaned_data["question_%s" % question.id].strip().lower(),
                    question.answer
            ):
                form.add_error(None, ValidationError(
                    _("One or more answers are incorrect"),
                    code="incorrect"
                ))
                return self.form_invalid(form)
        return super(ResetPasswordSecurityQuestionsView, self).form_valid(form)

    def get_success_url(self):
        user = models.CoreUser.objects.get(
            id=self.request.session["lookup_user_id"])
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return reverse(
            "password_reset_confirm",
            kwargs={"uidb64": uidb64, "token": token}
        )


defender_decorator = watch_login()
watch_login_method = method_decorator(defender_decorator)
ResetPasswordSecurityQuestionsView.dispatch = watch_login_method(
    ResetPasswordSecurityQuestionsView.dispatch)


class PasswordResetConfirmView(AnonUserRequiredMixin, PasswordResetConfirmView):
    form_class = forms.SetPasswordForm

    def form_valid(self, form):
        # This contains the HttpResponse for the success page.
        valid_response = super().form_valid(form)

        client_name = constants.get_theme_client_name(
            self.request
        )
        client_web_url = utils.get_session_data(
            self.request, constants.SessionKeys.CLIENT_WEBSITE
        )
        # If there is a client present, assume this user came from a
        # client site. However if the client has no website_url setup we can
        # not make an assumption on where the user needs to go back to.
        if client_name and client_web_url:

            # Render a success page that contains the website the user should
            # attempt to login from again. This is saner than the auth service
            # needing to persist the oidc authorise paramaters for the client.
            return render(
                self.request,
                "authentication_service/message.html",
                context={
                    "page_meta_title": _("Password update success"),
                    "page_title": _("Password update success"),
                    "page_message": mark_safe(_(
                        "Your password has been successfully updated,"
                        " please login again from:"
                        f" <a href='{client_web_url}'>{client_name}</a>"
                    )),
                }
            )
        return valid_response


class HealthCheckView(View):

    def get(self, request, *args, **kwargs):

        with connection.cursor() as cursor:
            cursor.execute("SELECT LOCALTIMESTAMP")
            db_timestamp = cursor.fetchone()[0]

        data = {
            "host": socket.getfqdn(),
            "server_timestamp": datetime.datetime.now(),
            "db_timestamp": db_timestamp,
            "version": pkg_resources.require("authentication_service")[0].version
        }

        return JsonResponse(data)


class MetricView(View):

    def get(self, request, *args, **kwargs):
        response = HttpResponse(prometheus_client.generate_latest(),
                                content_type=prometheus_client.CONTENT_TYPE_LATEST)
        return response
