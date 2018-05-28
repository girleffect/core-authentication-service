import datetime
import json
import logging

import jsonschema
from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.forms import HiddenInput

from authentication_service import exceptions
from authentication_service.constants import EXTRA_SESSION_KEY

DATE_DATETIME_RANGE_SCHEMA = {
    "type": "object",
    "properties": {
        "from": {
            "type": "string",
        },
        "to": {
            "type": "string",
        }
    },
    "minProperties": 1,
    "additionalProperties": False
}


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
            elif field.name == "logo":  # Client field
                result[field.name] = instance.logo.path if instance.logo else None
            elif field.name == "country":  # User field
                result[field.name] = instance.country.code if instance.country else None
            else:
                result[field.name] = getattr(instance, field.name)
    return result


def range_filter_parser(date_range: str):
    parsed_range = {}

    if isinstance(date_range, str):
        # Handle a string argument if JSON parse-able.
        try:
            date_range = json.loads(date_range, encoding="utf-8")
        except (ValueError, TypeError) as e:
            raise SuspiciousOperation(e)
    elif not isinstance(date_range, dict):
        raise exceptions.BadRequestException(
            f"Date range not an object or JSON string."
        )

    try:
        jsonschema.validate(date_range, DATE_DATETIME_RANGE_SCHEMA)
    except jsonschema.ValidationError as ve:
        raise exceptions.BadRequestException(
            f"Invalid date range specified: {ve.message}"
        )

    for key, date in date_range.items():
        # Preferable to not mix date and datetime objects, make sure all are
        # date objects.
        if date.lower() != "none":
            # Assumptions are made about the date format, based on swagger spec.
            # 2018-04-26T10:44:47.021Z
            try:
                if "T" in date:
                    formatted_date = datetime.datetime.strptime(
                        date.split(".")[0], "%Y-%m-%dT%H:%M:%S"
                    )
                else:
                    formatted_date = datetime.datetime.strptime(
                        date, "%Y-%m-%d"
                    ).date()
                parsed_range[key] = formatted_date
            except ValueError:
                raise exceptions.BadRequestException(
                    f"Date value({date}) does not have "
                    f"correct format: YYYY-MM-DD or YYYY-MM-DDTHH:MI:SS(.000)Z"
                )

    if not parsed_range:  # No limits specified
        raise exceptions.BadRequestException(
            f"At least one limit needs to be provided."
        )

    if "from" not in parsed_range:
        return {"lte": parsed_range["to"]}

    if "to" not in parsed_range:
        return {"gte": parsed_range["from"]}

    return {"gte": parsed_range["from"], "lte": parsed_range["to"]}


def update_session_data(request, key, data):
    if not request.session.get(EXTRA_SESSION_KEY, None):
        request.session[EXTRA_SESSION_KEY] = {}
    request.session[EXTRA_SESSION_KEY][key] = data


def get_session_data(request, key):
    return request.session.get(EXTRA_SESSION_KEY, {}).get(key, None)
