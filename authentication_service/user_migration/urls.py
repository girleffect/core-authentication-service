from django.conf.urls import url

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
]
