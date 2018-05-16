from datetime import date
from dateutil.relativedelta import relativedelta

from formtools.wizard.views import NamedUrlSessionWizardView

from django.contrib.auth import get_user_model
from django.core import signing
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.utils.functional import cached_property
from django.contrib.auth import login
from django.shortcuts import redirect

from authentication_service import forms, models, views
from authentication_service.decorators import generic_deprecation
from authentication_service.user_migration.forms import UserDataForm
from authentication_service.user_migration.models import (
    TemporaryMigrationUserStore
)


migration_forms = (
    ("userdata", UserDataForm),
    ("securityquestions", forms.SecurityQuestionFormSet),
)
class MigrateUserWizard(views.LanguageMixin, NamedUrlSessionWizardView):
    form_list = migration_forms
    instance_dict = {
        "securityquestions": models.SecurityQuestion.objects.none()
    }

    @generic_deprecation(
        "authentication_service.user_migration.MigrateUserWizard:" \
        " This view is temporary and should not be used or" \
        " subclassed."
    )
    def dispatch(self, *args, **kwargs):
        # TODO should store data on session storeage not self.
        self.token = self.kwargs["token"]
        # TODO pass along and store on wizard session
        # self.next = 

        try:
            self.temp_id = signing.loads(
                self.token,
                salt="ge-migration-user-registration",
                max_age=900 # 15 min in seconds
            )
        except signing.SignatureExpired:
            messages.error(
                self.request,
                _("Migration url has expired, please login again.")
            )
            # TODO pass next along and add next back in here.
            return HttpResponseRedirect(reverse("login"))

        # Super sets up storage.
        dispatch = super(MigrateUserWizard, self).dispatch(*args, **kwargs)
        query = self.request.GET.get("persist_query", None)

        # Wizard querystrings get stripped, this will ovalidate true once.
        # Change get_step_url to persist querystrings.
        if query:
            self.storage.extra_data["persist_query"] = query
        return dispatch

    def get_step_url(self, step):
        return reverse(
            f"user_migration:{self.url_name}",
            kwargs={
                "token": self.token,
                "step": step
            }
        )

    def get_form_kwargs(self, step=None):
        kwargs = {}
        if step == "securityquestions":
            kwargs["language"] = self.language
        return kwargs

    def get_form_initial(self, step):
        if step == "userdata":
            return {
                "username": self.get_user_data.username
            }
        return self.initial_dict.get(step, {})

    def done(self, form_list, **kwargs):
        cleaned_data = self.get_all_cleaned_data()
        user = get_user_model().objects.create_user(
            username=cleaned_data["username"],
            birth_date = date.today() - relativedelta(
                years=cleaned_data["age"]
            ),
            password=cleaned_data["password2"],
            migration_data = {
                "app_id": self.get_user_data.app_id,
                "site_id": self.get_user_data.site_id,
                "user_id": self.get_user_data.user_id,
                "username": self.get_user_data.username
            }
        )
        for form_data in cleaned_data["formset-securityquestions"]:
            # All fields on model are required, as such it requires the
            # full set of data.
            data = form_data
            data["user_id"] = user.id
            data["language_code"] = self.language
            question = models.UserSecurityQuestion.objects.create(**data)
        self.get_user_data.delete()
        login(self.request, user)
        query = self.storage.extra_data.get("persist_query", None)
        next_query = f"?next={query}" if query is not None else ""
        return redirect(f"{reverse('login')}{next_query}")

    @cached_property
    def get_user_data(self):
        try:
            return TemporaryMigrationUserStore.objects.get(
                id=self.temp_id
            )
        except TemporaryMigrationUserStore.DoesNotExist:
            raise Http404(
                f"Migrating user with id {self.temp_id} does not exist."
            )

