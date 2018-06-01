#!/bin/bash

ADDRESS_VALUE=${ADDRESS:=0.0.0.0:8000}

python manage.py migrate --noinput

# TODO: Run as own service in docker compose, qa and prod environments.
python manage.py compilemessages
python manage.py collectstatic --no-input
python manage.py runserver $ADDRESS_VALUE
