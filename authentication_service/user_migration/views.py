from datetime import date
from dateutil.relativedelta import relativedelta

from defender.decorators import watch_login
from formtools.wizard.views import NamedUrlSessionWizardView

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.core import signing
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils import translation
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.utils.translation import ugettext as _
from django.views.generic.edit import FormView

from authentication_service import forms, models, views
from authentication_service.decorators import generic_deprecation
from authentication_service.user_migration.forms import (
    UserDataForm, SecurityQuestionGateForm, PasswordResetForm
)
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
        "authentication_service.user_migration.MigrateUserWizard:"
        " This view is temporary and should not be used or"
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
                max_age=15*360  # 15 min in seconds
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
        kwargs = super(MigrateUserWizard, self).get_form_kwargs(step)
        if step == "securityquestions":
            kwargs["language"] = self.language
        return kwargs

    def get_form_initial(self, step):
        if step == "userdata":
            return {
                "username": self.migration_user.username
            }
        return self.initial_dict.get(step, {})

    def done(self, form_list, **kwargs):
        cleaned_data = self.get_all_cleaned_data()
        user = get_user_model().objects.create_user(
            username=cleaned_data["username"],
            birth_date=date.today() - relativedelta(
                years=cleaned_data["age"]
            ),
            password=cleaned_data["password2"],
            migration_data={
                "user_id": self.migration_user.user_id,
                "client_id": self.migration_user.client_id,
                "username": self.migration_user.username
            }
        )
        for form_data in cleaned_data["formset-securityquestions"]:
            # All fields on model are required, as such it requires the
            # full set of data.
            data = form_data
            data["user_id"] = user.id
            data["language_code"] = self.language
            models.UserSecurityQuestion.objects.create(**data)

        # Delete temporary migration data
        self.migration_user.delete()

        # Log new user in, allows for normal login flow to continue after
        # redirect
        login(self.request, user)
        return redirect(self.get_login_url())

    @cached_property
    def migration_user(self):
        try:
            return TemporaryMigrationUserStore.objects.get(
                id=self.migration_user_id
            )
        except TemporaryMigrationUserStore.DoesNotExist:
            raise Http404(
                f"Migrating user with id {self.migration_user_id} does not exist."
            )

    def get_login_url(self, query=None):
        # Do not rely on storage being present
        if hasattr(self, "storage"):
            query = self.storage.extra_data.get("persist_query", query)
        return query or reverse("login")


class QuestionGateView(FormView):
    form_class = SecurityQuestionGateForm
    template_name = "authentication_service/form.html"

    @generic_deprecation(
        "authentication_service.user_migration.QuestionGate:"
        " This view is temporary and should not be used or"
        " subclassed."
    )
    def dispatch(self, *args, **kwargs):
        self.token = self.kwargs["token"]

        # Check if token has expired
        try:
            self.migration_user_id = signing.loads(
                self.token,
                salt="ge-migration-user-pwd-reset",
                max_age=10*360  # 10 min in seconds
            )
        except signing.SignatureExpired:
            messages.error(
                self.request,
                _("Password reset url has expired,"
                    " please restart the password reset proces.")
            )
            return redirect(self.get_login_url())

        user = self.migration_user
        language = translation.get_language()
        if user.question_one and not user.question_one.get(language, None) \
                or user.question_two and not user.question_two.get(language, None):
            return TemplateResponse(
                self.request,
                "authentication_service/message.html",
                context={
                    "page_class": "Page-Not-Found",
                    "page_meta_title": _("Language not found"),
                    "page_title": _("Language not found"),
                    "page_message": _(
                        "No question translation matching the"
                        " current language could be found."
                    )
                },
                status=404
            )
        return super(QuestionGateView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(QuestionGateView, self).get_form_kwargs()
        kwargs["user"] = self.migration_user
        kwargs["language"] = translation.get_language()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(QuestionGateView, self).get_context_data(**kwargs)

        # Added context for django defender, needs correct template
        context["auth_username"] = self.migration_user.username
        context["defender_field_name"] = settings.DEFENDER_USERNAME_FORM_FIELD
        return context

    def form_valid(self, form):
        return self.get_success_url()

    @cached_property
    def migration_user(self):
        try:
            return TemporaryMigrationUserStore.objects.get(
                id=self.migration_user_id
            )
        except TemporaryMigrationUserStore.DoesNotExist:
            raise Http404(
                f"Migrating user with id {self.migration_user_id} does not exist."
            )

    def get_success_url(self, query=None):
        token = signing.dumps(
            self.migration_user.id, salt="ge-migration-user-pwd-gate-passed"
        )
        url = reverse(
            "user_migration:password_reset", kwargs={
                "token": token
            }
        )
        return redirect(url)

    # TODO query argument added in preperation for persisting the login
    # querystring and directing the user back into the proper login flow.
    def get_login_url(self, query=None):
        return reverse("login")


defender_decorator = watch_login()
watch_login_method = method_decorator(defender_decorator)
QuestionGateView.dispatch = watch_login_method(QuestionGateView.dispatch)


class PasswordResetView(FormView):
    form_class = PasswordResetForm
    template_name = "authentication_service/form.html"

    @generic_deprecation(
        "authentication_service.user_migration.PasswordReset:"
        " This view is temporary and should not be used or"
        " subclassed."
    )
    def dispatch(self, *args, **kwargs):
        self.token = self.kwargs["token"]

        # Check if token has expired
        try:
            self.migration_user_id = signing.loads(
                self.token,
                salt="ge-migration-user-pwd-gate-passed",
                max_age=5*360  # 5 min in seconds
            )
        except signing.SignatureExpired:
            messages.error(
                self.request,
                _("Password reset url has expired,"
                    " please restart the password reset proces.")
            )
            return redirect(self.get_login_url())
        return super(PasswordResetView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PasswordResetView, self).get_form_kwargs()
        user = self.migration_user
        kwargs["user"] = user
        return kwargs

    def form_valid(self, form):
        form.update_password()
        return self.get_success_url()

    @cached_property
    def migration_user(self):
        try:
            return TemporaryMigrationUserStore.objects.get(
                id=self.migration_user_id
            )
        except TemporaryMigrationUserStore.DoesNotExist:
            raise Http404(
                f"Migrating user with id {self.migration_user_id} does not exist."
            )

    def get_success_url(self, query=None):
        return redirect(reverse("password_reset_done"))

    # TODO query argument added in preperation for persisting the login
    # querystring and directing the user back into the proper login flow.
    def get_login_url(self, query=None):
        return reverse("login")
