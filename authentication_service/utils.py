import datetime
import json
import logging

from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.forms import HiddenInput

from authentication_service import exceptions
from authentication_service.constants import EXTRA_SESSION_KEY


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


def range_filter_parser(date_range):
    parsed_range = {}
    if isinstance(date_range, str):
        # Depending on the format of the dates inside, literal_eval will break.
        # Handle a string argument if JSON parse-able.
        try:
            date_range = json.loads(date_range, encoding="utf-8")
        except (ValueError, TypeError) as e:
            raise SuspiciousOperation(e)
    elif not isinstance(date_range, dict):
        raise exceptions.BadRequestException(
            f"Date range not an object or JSON string."
        )

    # On the off chance there are more or less than 2 entries in the list.
    if len(date_range) > 2:
        raise exceptions.BadRequestException(
            f"Date range object with length:"
            f"{len(date_range)}, exceeds max length of 2"
        )

    for key, date in date_range.items():
        # Preferable to not mix date and datetime objects, make sure all are
        # date objects.
        if isinstance(date, str) and date.lower() != "none":
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
                    )
                parsed_range[key] = formatted_date
            except ValueError:
                raise exceptions.BadRequestException(
                    f"Date value({date}) does not have "
                    f"correct format YYYY-MM-DD"
                )
        elif isinstance(date, datetime.datetime) or isinstance(
                date, datetime.date):
            parsed_range[key] = date
        else:
            parsed_range[key] = None

    # Should contain at least one not NoneType object.
    parsed_values = [value for value in parsed_range.values()]
    if any(parsed_values):
        # We need to pass some hints along to the caller. __range does not
        # support [,date]/[date,]
        if not parsed_range.get("from"):
            parsed_range = ("lte", parsed_range["to"])
        elif not parsed_range.get("to"):
            parsed_range = ("gte", parsed_range["from"])
        else:
            parsed_range = ("range", parsed_values)
    else:
        raise exceptions.BadRequestException(
            "Date range object does not contain any date object values"
        )

    return parsed_range


def update_session(request, key, data):
    if not request.session.get(EXTRA_SESSION_KEY, None):
        request.session[EXTRA_SESSION_KEY] = {}
    request.session[EXTRA_SESSION_KEY][key] = data


def get_session_data(request, key):
    return request.session.get(EXTRA_SESSION_KEY, {}).get(key, None)
