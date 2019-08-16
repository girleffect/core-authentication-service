from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm

from oidc_provider.models import UserConsent

from authentication_service import models


class ExtendedCreationForm(UserCreationForm):
    fields = ("username", "birth_date", "email", "msisdn", "organisation")


@admin.register(models.CoreUser)
class CoreUserAdmin(UserAdmin):
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Additional required fields", {
            "fields": ("birth_date",),
        }),
        ("Additional fields", {
            "fields": ("email", "msisdn", "organisation"),
        }),
    )
    add_form = ExtendedCreationForm
    fieldsets = UserAdmin.fieldsets + (
        ("Extra data",
            {"fields": (
                "nickname", "msisdn", "birth_date", "country", "avatar",
                "email_verified", "msisdn_verified", "organisation"
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


class UserSiteAdmin(admin.ModelAdmin):
    fields = ["user", "site_id", "consented_at", "created_at", "updated_at"]
    readonly_fields = ["consented_at", "created_at", "updated_at"]
    list_display = fields


class UserConsentAdmin(admin.ModelAdmin):
    list_display = ['user', 'client', 'date_given', 'expires_at']
    search_fields = ['user__username', 'user__email', 'client__name']
    list_filter = ['client__name', 'client__client_type', 'date_given', 'expires_at']


admin.site.register(models.Country, admin.ModelAdmin)
admin.site.register(models.UserSecurityQuestion, admin.ModelAdmin)
admin.site.register(models.SecurityQuestion, SecurityQuestionForm)
admin.site.register(models.QuestionLanguageText, admin.ModelAdmin)
admin.site.register(models.Organisation, admin.ModelAdmin)
admin.site.register(models.UserSite, UserSiteAdmin)
admin.site.register(UserConsent, UserConsentAdmin)
