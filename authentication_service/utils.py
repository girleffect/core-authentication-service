from django.conf import settings
from django.core.exceptions import ValidationError, SuspiciousOperation
from django.forms import HiddenInput
from django.http import HttpResponseBadRequest


def update_form_fields(form, required=None, hidden=None, validators=None, fields_data=None):
    """Update form fields and widgets.

    form --  Instance of a form.
    required -- list of fields to toggle required for.
    hidden -- list of fields to hide.
    validators -- a dictionary
        {
            "<fieldname>": [<list of validators>]
        }
    fields_data -- a dictionary
        {
            "<fieldname>": {
                "attributes": {
                    <attribute>: <value>
                },
            }
        }

    Helper method for setting field and widget attributes, can
    be used for any form instance. Sets attributes on both fields and widgets.
    """
    required = required or []
    hidden = hidden or []
    validators = validators or {}
    fields_data = fields_data or {}

    # Mark fields as required on both the form and widget
    for field in required:
        form.fields[field].required = True
        form.fields[field].widget.is_required = True

    # Mark fields as hidden on the widget
    for field in hidden:
        form.fields[field].widget = HiddenInput()

    # Set validators on fields.
    for field, data in validators.items():
        form.fields[field].validators = data

    # Update field and widget attributes.
    for field, data in fields_data.items():
        if data.get("attributes", None):
            widget = form.fields[field].widget
            field = form.fields[field]

            # Special case, allow for the assignment of a different input type.
            if data["attributes"].get("type"):
                widget.input_type = data["attributes"].pop(
                    "type", widget.input_type
                )

            # Widgets for the most part make use of a dictionary structure, so
            # just update the dictionary blindly.
            widget.attrs.update(data["attributes"])

            # Fields make use of instance attributes, so it requires a
            # different approach.
            for attr, val in data["attributes"].items():
                setattr(field, attr, val)


def check_limit(limit):
    """ Ensures the limit is within bounds or sets the default limit if no limit
    was specified.
    :param limit: Amount of objects to return.
    :return: Either the minimum, maximum or the default limit.
    """
    if limit:
        limit = int(limit)
        if limit > settings.MAX_LISTING_LIMIT or \
                limit < settings.MIN_LISTING_LIMIT:
            # SuspiciousOperation raises 400 bad request in Django 1.11.
            # https://docs.djangoproject.com/en/1.11/ref/views/#the-400-bad-request-view
            raise SuspiciousOperation()
        return limit
    return settings.DEFAULT_LISTING_LIMIT


def strip_empty_optional_fields(object_dict):
    """ We do not need to add fields that contain None to the response,
    so we strip those fields out of the response. To do this, we iterate over
    the fields in the input dictionary and check that the value isn't, what we
    consider, empty. If a field has a value, add that field and value to the
    output dictionary.
    :param object_dict: Input dictionary containing possible empty fields.
    :return: Output dictionary containing only fields that have values.
    """
    return {k: v for k, v in object_dict.items() if v is not None}


def to_dict_with_custom_fields(instance, custom_fields):
    """ Convert an object to a dictionary with only some of the fields that
    exist on the object. Some fields also require some manual handling.
    :param instance: Object to be converted.
    :param custom_fields: List of fields to include in dict.
    :return: Dictionary with custom fields.
    """
    result = {}
    for field in instance._meta.fields:
        if field.name in custom_fields:
            if field.name == "avatar":  # CoreUser field
                result[field.name] = instance.avatar.path if instance.avatar else None
            else:
                result[field.name] = getattr(instance, field.name)
    return result
