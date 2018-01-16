from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.views.generic.edit import CreateView, FormView

from core_authentication_service import forms, models


REDIRECT_COOKIE_KEY = "register_redirect"


class RegistrationView(CreateView):
    template_name = "core_authentication_service/registration/registration.html"
    form_class = forms.RegistrationForm

    def dispatch(self, *args, **kwargs):
        # Grab language off of querystring first. Otherwise default to django
        # middleware set one.
        self.language = self.request.GET.get("language") \
            if self.request.GET.get("language") else self.request.LANGUAGE_CODE
        self.redirect_url = self.request.GET.get("redirect_url")
        self.theme = self.request.GET.get("theme")
        return super(RegistrationView, self).dispatch(*args, **kwargs)

    def get_template_names(self):
        template_names = []

        # Allow for possible sub classing of view without needing extra work to
        # assign base template.
        if self.template_name is not None:
            template_names = [self.template_name]

        # Any extra templates need to be before the base.
        template_names = [
            "core_authentication_service/registration/registration_%s.html" % self.theme,
        ] + template_names
        return template_names

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

        # Do some work and assign questions to the user.
        for form in formset.forms:
            # Trust that form did its work. In the event that not all questions
            # were answered, save what can be saved.
            if form.cleaned_data.get(
                    "answer", None) and form.cleaned_data.get(
                    "question", None):
                question = models.UserSecurityQuestion.objects.create(**form.cleaned_data)
                question.language_code = self.language
                question.user = self.object
                question.save()

        if self.redirect_url:
            response.set_cookie(
                REDIRECT_COOKIE_KEY, value=self.redirect_url, httponly=True
            )
        return response

    def get_success_url(self):
        url = settings.LOGIN_URL
        if self.security == "high" or self.request.GET.get(
                "show2fa") == "true":
            url =reverse("two_factor_auth:setup")
        elif self.redirect_url:
            url = self.redirect_url
        return url


# Class based view for more flwxibility if needed.
class RedirectView(View):
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
