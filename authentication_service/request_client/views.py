from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin, AccessMixin
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView

from authentication_service.request_client import forms


class RequestCientView(UserPassesTestMixin, AccessMixin, CreateView):
    template_name = "authentication_service/form.html"
    form_class = forms.RequestClientForm
    raise_exception = True

    def test_func(self):
        user = self.request.user
        if user.organisation or user.is_superuser:
            return True
        else:
            return False

    def form_valid(self, form):
        # Add current user to form instance, before checking form validity and
        # allowing it to save the instance.
        form.instance.requesting_user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        messages.add_message(
            self.request, messages.SUCCESS, _("Request successfully sent."))
        return reverse("edit_profile")
