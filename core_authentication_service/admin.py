from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core_authentication_service import models

@admin.register(models.CoreUser)
class CoreUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Extra data",
            {"fields": (
                "nickname", "msisd", "birth_date", "country_code", "avatar"
            )}
        ),
    )

admin.site.register(models.Country, admin.ModelAdmin)
admin.site.register(models.UserSecurityQuestion, admin.ModelAdmin)
admin.site.register(models.SecurityQuestion, admin.ModelAdmin)
admin.site.register(models.QuestionLaguageText, admin.ModelAdmin)
