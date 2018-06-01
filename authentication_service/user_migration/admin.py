from django.contrib import admin

from authentication_service.user_migration.models import (
    TemporaryMigrationUserStore
)
# Register your models here.

# TODO should either be removed from admin or made read only
admin.site.register(TemporaryMigrationUserStore)
