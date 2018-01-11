from django.views.generic.edit import CreateView, FormView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from core_authentication_service import forms


class RegistrationView(CreateView):
    template_name = "core_authentication_service/registration.html"
    form_class = forms.RegistrationForm
    success_url = "/"

    # TODO:
    #   - Add security question models, multi language questions.
    #   - Logic for msisdn and email required.
    #   - Split high and none security requirements.
    #   - Handle required field querystring value.
    #   - Add 2FA to flow.
    #   - Handle theme querystring value, will need to effect 2FA templates as well.
    #   - Make it optional, but enforce able as required.
    #   - Will need to check client_id as provided for oidc login, for redirects not on domain. Validate client_id and redirect_uri before rendering form.
    #   - Add basis for invitation handling.
