"""
Do not modify this file. It is generated from the Swagger specification.

If you need to tweak the functionality in this file, you can replace it
with your own.
"""
from functools import wraps
import base64
import json
import jsonschema
import os
import sys

from django.contrib.auth import authenticate, login
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponse
from django.conf import settings


def body_to_dict(body, schema):
    # type: (str, Dict) -> Dict
    """

    :param body: The body content
    :param schema: The expected JSONSchema
    :return: A dictionary containing the parsed body
    :raises SuspiciousOperation: If the body is not in JSON format, or does not
       conform to the specified schema.
    """
    try:
        data = json.loads(body)
        jsonschema.validate(data, schema=schema)
        return data
    except Exception as e:
        # The SuspiciousOperation exception will result in an
        # HttpResponseBadRequest response.
        raise SuspiciousOperation(e)


def login_required_no_redirect(view_func):
    """
    Helper function that returns an HTTP 401 response if the user making the
    request is not logged in, or did not provide basic HTTP authentication in
    the request.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # For API calls, the only authentication mechanism allowed is the API key
        if "HTTP_X_API_KEY" in request.META:
            key = request.META["HTTP_X_API_KEY"]
            if key in settings.ALLOWED_API_KEYS:
                return view_func(request, *args, **kwargs)

        return HttpResponse("Unauthorized", status=401)

    return wrapper