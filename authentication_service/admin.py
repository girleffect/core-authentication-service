from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from authentication_service import models


@admin.register(models.CoreUser)
class CoreUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Extra data",
            {"fields": (
                "nickname", "msisdn", "birth_date", "country", "avatar",
                "email_verified", "msisdn_verified"
            )}
        ),
    )


class QuestionTextInline(admin.TabularInline):
    model = models.QuestionLanguageText
    extra = 0
    fields = ["language_code", "question_text"]


class SecurityQuestionForm(admin.ModelAdmin):
    inlines = [
        QuestionTextInline,
    ]


admin.site.register(models.Country, admin.ModelAdmin)
admin.site.register(models.UserSecurityQuestion, admin.ModelAdmin)
admin.site.register(models.SecurityQuestion, SecurityQuestionForm)
admin.site.register(models.QuestionLanguageText, admin.ModelAdmin)
