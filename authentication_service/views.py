from defender.decorators import watch_login
from defender.utils import REDIS_SERVER, get_username_attempt_cache_key, \
    get_username_blocked_cache_key

from django.conf import settings
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.forms import formset_factory
from django.forms.formsets import BaseFormSet
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.views.generic.edit import CreateView, UpdateView, FormView
from two_factor.forms import AuthenticationTokenForm
from two_factor.forms import BackupTokenForm

from two_factor.utils import default_device
from two_factor.views import core

from authentication_service import forms, models


class ThemeMixin:
    """This mixin gets the theme parameter from a request URL, if it exists, and
    sets the appropriate template.
    """
    TEMPLATE_PREFIX = ""
    theme = None

    def dispatch(self, *args, **kwargs):
        self.theme = self.request.GET.get("theme")
        return super(ThemeMixin, self).dispatch(*args, **kwargs)

    def get_template_names(self):
        template_names = []

        if self.template_name is not None:
            template_names = [self.template_name]

        # Any extra templates need to be before the base.
        template_names = [
            "%s%s%s.html" % (
                self.TEMPLATE_PREFIX,
                "_" if self.TEMPLATE_PREFIX else "",
                self.theme
            ),
        ] + template_names
        return template_names


class RedirectMixin:
    """This mixin gets the redirect URL parameter from the request URL. This URL
    is used as the success_url attribute. If no redirect_url is set, it will
    default to the Login URL.

    For registration, this mixin also checks the security level of the request.
    If the security level is high, the success URL will redirect to 2FA setup.

    TODO: Security should be moved out.
    """
    def dispatch(self, *args, **kwargs):
        self.redirect_url = self.request.GET.get("redirect_url")
        return super(RedirectMixin, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        url = settings.LOGIN_URL
        if hasattr(
                self, "security"
        ) and self.security == "high" or self.request.GET.get(
                "show2fa") == "true":
            url = reverse("two_factor_auth:setup")
        elif self.redirect_url:
            url = self.redirect_url
        return url


class LockoutView(View):
    """
    A view used by Defender to inform the user that they have exceeded the
    threshold for allowed login failures or password reset attempts.
    """
    template_name = "authentication_service/lockout.html"


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

    def __init__(self, **kwargs):
        super(LoginView, self).__init__(**kwargs)
        # This is a workaround for the following issue:
        # https://github.com/kencochrane/django-defender/issues/110
        # We should be able to remove this when the issue is fixed.
        pipe = REDIS_SERVER.pipeline()
        pipe.delete(get_username_attempt_cache_key(None))
        pipe.delete(get_username_blocked_cache_key(None))
        pipe.execute()


# Protect the login view using Defender. Defender provides a method decorator
# which we have to tweak to apply to the dispatch method of a view.
# This is based on their own implementation of their middleware class:
# https://github.com/kencochrane/django-defender/blob/master/defender/middleware.py#L24-L27
defender_decorator = watch_login()
watch_login_method = method_decorator(defender_decorator)
LoginView.dispatch = watch_login_method(LoginView.dispatch)
# TODO: Do something similar to the password reset view when it is implemented.


REDIRECT_COOKIE_KEY = "register_redirect"


class RegistrationView(ThemeMixin, RedirectMixin, CreateView):
    TEMPLATE_PREFIX = "authentication_service/registration/registration"
    template_name = "authentication_service/registration/registration.html"
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
        # TODO at later stage, check if this needs to be validated against oidc
        # clients as well.
        url = request.COOKIES.get(REDIRECT_COOKIE_KEY)

        # Default fallback if cookie was deleted or no url was set.
        response = HttpResponseRedirect(settings.LOGIN_URL)
        if url:
            response = HttpResponseRedirect(url)

        response.delete_cookie(REDIRECT_COOKIE_KEY)
        logout(request)
        return response


class EditProfileView(ThemeMixin, RedirectMixin, UpdateView):
    TEMPLATE_PREFIX = "authentication_service/profile/edit_profile"
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


class UpdatePasswordView(ThemeMixin, RedirectMixin, UpdateView):
    TEMPLATE_PREFIX = "authentication_service/profile/update_password"
    template_name = "authentication_service/profile/update_password.html"
    form_class = PasswordChangeForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super(UpdatePasswordView, self).get_form_kwargs()
        kwargs["user"] = kwargs.pop("instance")
        return kwargs

    def form_valid(self, form):
        if form.is_valid():
            update_session_auth_hash(self.request, form.save())
        super(UpdatePasswordView, self).form_valid(form)


class UpdateSecurityQuestionsView(ThemeMixin, RedirectMixin, FormView):
    TEMPLATE_PREFIX = "authentication_service/profile/update_security_questions"
    template_name = \
        "authentication_service/profile/update_security_questions.html"
    form_class = forms.UpdateSecurityQuestionsForm
    QuestionFormSet = formset_factory(
        forms.UpdateSecurityQuestionsForm(), BaseFormSet)

    def get_form_kwargs(self):
        kwargs = super(UpdateSecurityQuestionsView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(
            UpdateSecurityQuestionsView, self).get_context_data(**kwargs)
        context["question_formset"] = self.QuestionFormSet
        return context
