# TODO See if this is needed, settings might need to move so as to not end up with relative path imports.
"""
WSGI config for core_authentication_service project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core_authentication_service.settings")

application = get_wsgi_application()
