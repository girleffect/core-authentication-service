from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import CreateView

from authentication_service.user_migration import views
from authentication_service.user_migration.forms import CreateTempUserForm


migration_wizard = views.MigrateUserWizard.as_view(
    url_name="migrate_user_step"
)

urlpatterns = [
    # Migrate user wizard
    url(
        r"^migrate/(?P<token>[\w:-]+)/(?P<step>.+)/$",
        migration_wizard,
        name="migrate_user_step"
    ),
    url(r"^migrate/(?P<token>[\w:-]+)/$", migration_wizard, name="migrate_user"),

    # TODO remove after integration work is done
    url(
        r"^create-temp-user/$",
        login_required(CreateView.as_view(
            form_class=CreateTempUserForm,
            template_name="user_migration/creation_form.html",
            success_url=reverse_lazy("user_migration:temp_creation")
        )),
        name="temp_creation"
    )
]
