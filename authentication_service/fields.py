from django.forms.fields import Field
from django.utils.text import mark_safe
from django.utils.translation import ugettext as _

from authentication_service import widgets


class ParagraphField(Field):
    widget = widgets.ParagraphWidget
    queryset = None

    def __init__(self, paragraph=None, *args, **kwargs):
        # Sometimes the field being overriden is a ModelChoice, having the
        # queryset later could be useful.
        self.queryset = kwargs.pop("queryset", None)

        # Allow the ParagraphField to replace more advanced fields without
        # erroring.
        diff = set(kwargs) - set(dir(super(ParagraphField, self)))
        for kwarg in diff:
            kwargs.pop(kwarg, None)

        # Call super with trimmed kwargs
        super().__init__(*args, **kwargs)

        # Always empty out label for a paragraph field.
        self.label = ""

        # No matter what is set, this field should never be required.
        self.required = False
        self.widget.is_required = False

        # Fields should handle their own args not being set.
        if paragraph is None:
            paragraph = _("Please set a value for this field.")

        data = {
            "base_attrs": self.widget.attrs,
            "extra_attrs": {"paragraph": paragraph}
        }
        attrs = self.widget.build_attrs(**data)
        self.widget.attrs = attrs
