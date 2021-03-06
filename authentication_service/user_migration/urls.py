from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import CreateView

from authentication_service.user_migration import views


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
    url(
        r"^question-gate/(?P<token>[\w:-]+)/$",
        views.QuestionGateView.as_view(),
        name="question_gate"
    ),
    url(
        r"^password-reset/(?P<token>[\w:-]+)/$",
        views.PasswordResetView.as_view(),
        name="password_reset"
    ),
]
