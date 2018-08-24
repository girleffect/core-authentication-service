from django import forms
from django.contrib import admin

from authentication_service.user_migration.models import (
    TemporaryMigrationUserStore
)


class MigrationUserForm(forms.ModelForm):
    model = TemporaryMigrationUserStore

    class Meta:
        labels = {
            "pw_hash": "password hash"
        }
        help_texts = {
            "question_one": (
                "JSON field for security questions:"
                " {'language_code': 'question_text', ...}"
            ),
            "question_two":  (
                "JSON field for security questions:"
                " {'language_code': 'question_text', ...}"
            ),
            "pw_hash": (
                "This field should contain the password hash,"
                " if this is a new instance the password will be"
                " hashed on the first save. This field will be"
                " re-hashed if the value is changed in any"
                " way for subsequent saves."
            ),
            "answer_one": (
                "This field should contain the answer hash,"
                " if it was previously empty or changed it will be re-hashed"
            ),
            "answer_two": (
                "This field should contain the answer hash,"
                " if it was previously empty or changed it will be re-hashed"
            )
        }

    # Hash certain cleaned_data values, before instance is created or updated
    def _post_clean(self):
        # List of fields that require hashed values to be saved.
        # ("<field_name>", <bool_clean_and_lower>)
        hash_cleaned_data_fields = [
            ("pw_hash", False),
            ("answer_one", True),
            ("answer_two", True)
        ]

        for field, clean in hash_cleaned_data_fields:
            # Check if field value has actually changed
            if field in self.changed_data:
                value = self.cleaned_data[field]
                if clean:
                    value = value.strip().lower()
                self.cleaned_data[field] = self.instance.get_hash_value(value)

        # Let super do its work, this will assign the correct values to the
        # instance based on cleaned_data values.
        super()._post_clean()

class MigrationUserAdmin(admin.ModelAdmin):
    form = MigrationUserForm
    list_display = ("user_id", "client", "username")
    fieldsets = (
        ("Required data:", {
            "fields": ["username", "pw_hash", "user_id", "client"]
        }),
        ("Optional password reset data:", {
            "fields": ["question_one", "answer_one", "question_two", "answer_two"]
        })
    )

admin.site.register(TemporaryMigrationUserStore, MigrationUserAdmin)
