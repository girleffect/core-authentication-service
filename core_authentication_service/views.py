from django.views.generic.edit import CreateView, FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from core_authentication_service import forms


class RegistrationView(CreateView):
    template_name = "core_authentication_service/registration.html"
    form_class = forms.RegistrationForm
    success_url = "/"

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
        if kwargs.get("question_formset"):
            ct["question_formset"] = kwargs["question_formset"]
        else:
            ct["question_formset"] = forms.SecurityQuestionFormSet()
        return ct

    def form_invalid(self, form):
        formset = forms.SecurityQuestionFormSet(self.request.POST)
        return self.render_to_response(self.get_context_data(
            form=form, question_formset=formset
        ))

    def form_valid(self, form):
        formset = forms.SecurityQuestionFormSet(self.request.POST)

        if not formset.is_valid() or not form.is_valid():
            return self.render_to_response(self.get_context_data(
                form=form, question_formset=formset)
            )
        #return super(RegistrationView, self).form_valid(form)

    # TODO:
    #   - Move question query up one level to management form class, not form.
    #   - i18l setup.
    #   - Add 2FA to flow.
    #   - Handle theme querystring value, will need to effect 2FA templates as well.
    #   - Make it optional, but enforce able as required.
    #   - Will need to check client_id as provided for oidc login, for redirects not on domain. Validate client_id and redirect_uri before rendering form.
    #   - Listen to redirect_url.
    #   - Add basis for invitation handling.
