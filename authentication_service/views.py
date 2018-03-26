import json

from defender.decorators import watch_login
from defender.utils import REDIS_SERVER, get_username_attempt_cache_key, \
    get_username_blocked_cache_key

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash, \
    hashers, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordChangeView
)
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse, reverse_lazy
from django.forms.utils import ErrorList
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext as _
from django.views.generic import View, TemplateView
from django.views.generic.edit import CreateView, UpdateView, FormView

from two_factor.forms import AuthenticationTokenForm
from two_factor.forms import BackupTokenForm
from two_factor.utils import default_device
from two_factor.views import core

from authentication_service import forms, models, tasks, constants


REDIRECT_COOKIE_KEY = constants.COOKIES["redirect_cookie"]

class LanguageMixin:
    """This mixin sets an instance variable called self.language, value is
    passed in via url or determined by django language middleware
    """

    def dispatch(self, *args, **kwargs):
        self.language = self.request.GET.get("language") \
            if self.request.GET.get("language") else self.request.LANGUAGE_CODE
        return super(LanguageMixin, self).dispatch(*args, **kwargs)


class RedirectMixin:
    """This mixin gets the redirect URL parameter from the request URL. This URL
    is used as the success_url attribute. If no redirect_url is set, it will
    default to the Login URL.

    For registration, this mixin also checks the security level of the request.
    If the security level is high, the success URL will redirect to 2FA setup.

    TODO: Security should be moved out.
    """
    success_url = None

    def dispatch(self, *args, **kwargs):
        self.redirect_url = self.request.COOKIES.get(REDIRECT_COOKIE_KEY)
        return super(RedirectMixin, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        url = settings.LOGIN_URL
        if hasattr(
                self, "security"
        ) and self.security == "high" or self.request.GET.get(
                "show2fa") == "true":
            url = reverse("two_factor_auth:setup")
        elif self.success_url:
            url = self.success_url
        elif self.redirect_url:
            url = self.redirect_url
        return url


class LanguageRedirectMixin(LanguageMixin, RedirectMixin):
    """
    Combined class for the frequently used Language and Redirect mixins.
    Language can safely be set on views that make no use of it.
    """


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


class LoginView(core.LoginView):
    """This view simply extends the LoginView from two_factor.views.core. We
    only override the template and the done step, which we use to login
    superusers.
    """
    template_name = "authentication_service/login.html"

    form_list = (
        ('auth', AuthenticationForm),
        ('token', AuthenticationTokenForm),
        ('backup', BackupTokenForm),
    )


# Protect the login view using Defender. Defender provides a method decorator
# which we have to tweak to apply to the dispatch method of a view.
# This is based on their own implementation of their middleware class:
# https://github.com/kencochrane/django-defender/blob/master/defender/middleware.py#L24-L27
defender_decorator = watch_login()
watch_login_method = method_decorator(defender_decorator)
LoginView.dispatch = watch_login_method(LoginView.dispatch)
# TODO: Do something similar to the password reset view when it is implemented.


class RegistrationView(LanguageRedirectMixin, CreateView):
    template_name = "authentication_service/registration.html"
    form_class = forms.RegistrationForm
    security = None

    def dispatch(self, *args, **kwargs):
        # Grab language off of querystring first. Otherwise default to django
        # middleware set one.
        self.language = self.request.GET.get("language") \
            if self.request.GET.get("language") else self.request.LANGUAGE_CODE
        return super(RegistrationView, self).dispatch(*args, **kwargs)

    @property
    def get_formset(self):
        formset = forms.SecurityQuestionFormSet(language=self.language)
        if self.request.POST:
            formset = forms.SecurityQuestionFormSet(
                data=self.request.POST, language=self.language
            )
        return formset

    def get_form_kwargs(self):
        kwargs = super(RegistrationView, self).get_form_kwargs()
        self.security = self.request.GET.get("security")
        if isinstance(self.security, str):
            kwargs["security"] = self.security.lower()

        required = self.request.GET.getlist("requires")
        if required:
            kwargs["required"] = required

        hidden = self.request.GET.getlist("hide")
        if hidden:
            kwargs["hidden"] = hidden

        return kwargs

    def get_context_data(self, *args, **kwargs):
        ct = super(RegistrationView, self).get_context_data(*args, **kwargs)

        # Either a new formset instance or an existing one is passed to the
        # formset class.
        if kwargs.get("question_formset"):
            ct["question_formset"] = kwargs["question_formset"]
        else:
            ct["question_formset"] = self.get_formset
        return ct

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(
            form=form, question_formset=self.get_formset
        ))

    def form_valid(self, form):
        formset = self.get_formset

        if not formset.is_valid():
            return self.render_to_response(self.get_context_data(
                form=form, question_formset=formset)
            )

        # Let the user model save.
        response = super(RegistrationView, self).form_valid(form)

        # When we need to show the option to enable 2FA the newly created
        # user must be logged in.
        if self.security == "high" or self.request.GET.get("show2fa") == "true":
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'])
            login(self.request, new_user)

        # Do some work and assign questions to the user.
        for form in formset.forms:
            # Trust that form did its work. In the event that not all questions
            # were answered, save what can be saved.
            if form.cleaned_data.get(
                    "answer", None) and form.cleaned_data.get(
                    "question", None):

                # All fields on model are required, as such it requires the
                # full set of data.
                data = form.cleaned_data
                data["user_id"] = self.object.id
                data["language_code"] = self.language
                question = models.UserSecurityQuestion.objects.create(**data)

        if self.redirect_url:
            response.set_cookie(
                REDIRECT_COOKIE_KEY, value=self.redirect_url, httponly=True
            )
        return response


class CookieRedirectView(View):
    """
    Simple view that redirects in the event the client passes a cookie
    containing the correct key. In the event a cookie is not present, redirect
    to the django default login url.

    User is explicitly logged out to clear the user session. In anticipation
    that the referrer will prompt them to login again so as to obtain the oidc
    tokens.
    """
    def dispatch(self, request, *args, **kwargs):
        # No need for super, this view should at this stage not need any of its
        # http method functions.
        logout(request)
        url = request.COOKIES.get(REDIRECT_COOKIE_KEY)

        # Default fallback if cookie was deleted or no url was set.
        response = HttpResponseRedirect(settings.LOGIN_URL)
        if url:
            response = HttpResponseRedirect(url)

        response.delete_cookie(REDIRECT_COOKIE_KEY)
        return response


class EditProfileView(LanguageRedirectMixin, UpdateView):
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


class UpdatePasswordView(LanguageRedirectMixin, PasswordChangeView):
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


class UpdateSecurityQuestionsView(LanguageRedirectMixin, TemplateView):
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
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.render(request, formset)


class DeleteAccountView(FormView):
    template_name = "authentication_service/profile/delete_account.html"
    form_class = forms.DeleteAccountForm
    success_url = reverse_lazy("edit_profile")

    def dispatch(self, *args, **kwargs):
        if self.request.user.email is None and self.request.user.msisdn is None:
            messages.error(self.request,
                _("You require either an email or msisdn "
                "to request an account deletion")
            )
            return HttpResponseRedirect(self.get_success_url())
        return super(DeleteAccountView, self).dispatch(*args, **kwargs)

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
                    "context":{"reason": form.cleaned_data["reason"]},
                    "mail_type": "delete_account",
                    "objects_to_fetch": [user]
                }
            )
            messages.success(self.request, _("Successfully requested account deletion."))
            return super(DeleteAccountView, self).form_valid(form)


class ResetPasswordView(PasswordResetView):
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


class PasswordResetConfirmView(PasswordResetConfirmView):
    form_class = forms.SetPasswordForm
