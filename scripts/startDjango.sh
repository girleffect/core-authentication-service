#!/usr/bin/env sh
set -e

# The kinesis producer/consumer module creates extra processes that halts
# management commands as it does not auto terminate.
BUILDER=true python manage.py migrate --noinput

# With the current time constraints, reverted to starting Django via management
# command. See: https://praekeltorg.atlassian.net/browse/GEINFRA-361
python manage.py runserver 0.0.0.0:8000

# Command that needs to be used instead of runserver
#project.wsgi:application --threads 5 --timeout 50
