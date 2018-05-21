from datetime import date
from dateutil.relativedelta import relativedelta
import urllib

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
        self.token = self.kwargs["token"]

        # Grab the query early, for use in the event the token has expired
        query = self.request.GET.get("persist_query", None)

        # Check if token has expired
        try:
            self.migration_user_id = signing.loads(
                self.token,
                salt="ge-migration-user-registration",
                max_age=15*360 # 15 min in seconds
            )
        except signing.SignatureExpired:
            messages.error(
                self.request,
                _("Migration url has expired, please login again.")
            )
            return redirect(self.get_login_url(query=query))

        # Super sets up storage, needs to happen after token has been checked
        dispatch = super(MigrateUserWizard, self).dispatch(*args, **kwargs)

        # Querystrings are not persisted on wizard urls, unless work is done in
        # get_step_url to explicitly persist them. We opted to rather
        # store it in the wizard storage. Under those default conditions, this
        # if statement will only ever validate true once.
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

        # Delete temporary migration data
        self.get_user_data.delete()

        # Log new user in, allows for normal login flow to continue after
        # redirect
        login(self.request, user)
        return self.get_login_url()

    @cached_property
    def get_user_data(self):
        try:
            return TemporaryMigrationUserStore.objects.get(
                id=self.migration_user_id
            )
        except TemporaryMigrationUserStore.DoesNotExist:
            raise Http404(
                f"Migrating user with id {self.migration_user_id} does not exist."
            )

    def get_login_url(self, query=None):
        query = self.storage.extra_data.get("persist_query", query)
        return redirect(query or reverse("login"))
