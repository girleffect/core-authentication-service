from django.contrib import messages
from django.urls import reverse
from django.views.generic.edit import CreateView

from authentication_service.request_client import forms


class RequestCientView(CreateView):
    template_name = "authentication_service/form.html"
    form_class = forms.RequestClientForm

    def form_valid(self, form):
        # Add current user to form instance, before checking form validity and
        # allowing it to save the instance.
        form.instance.requesting_user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        messages.add_message(self.request, messages.SUCCESS, "Request successfully sent.")
        return reverse("edit_profile")
