#!/usr/bin/env sh
set -e

# The Kinesis producer/consumer module creates extra processes that halts
# management commands as it does not auto terminate.
BUILDER=true USE_KINESIS_PRODUCER=false python manage.py migrate --noinput

# The --threads parameter is required, otherwise the application won't start.
# It looks like, when omitted, it tries to spawn multiple processes which does
# not work.
/scripts/django-entrypoint.sh project.wsgi:application --threads 5 --timeout 50
