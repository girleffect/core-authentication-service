from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core_authentication_service.models import CoreUser

@admin.register(CoreUser)
class CoreUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Extra data",
            {"fields": (
                "nickname", "msisd", "birth_date", "country_code", "avatar"
            )}
        ),
    )
