from django.views.generic.edit import CreateView, FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from core_authentication_service import forms, models


class RegistrationView(CreateView):
    template_name = "core_authentication_service/registration.html"
    form_class = forms.RegistrationForm
    success_url = "/"

    def dispatch(self, *args, **kwargs):
        # Grab language off of querystring first else default to django
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
        security = self.request.GET.get("security")
        if isinstance(security, str):
            kwargs["security"] = security.lower()

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
            question = models.UserSecurityQuestion.objects.create(**form.cleaned_data)
            question.language_code = self.language
            question.user = self.object
            question.save()
        return response

    # TODO:
    #   - Add 2FA to flow.
    #   - Handle theme querystring value, will need to effect 2FA templates as well.
    #   - Make it optional, but enforce able as required.
    #   - Will need to check client_id as provided for oidc login, for redirects not on domain. Validate client_id and redirect_uri before rendering form.
    #   - Listen to redirect_url.
    #   - Add basis for invitation handling.
