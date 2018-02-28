#!/bin/bash

ADDRESS_VALUE=${ADDRESS:=0.0.0.0:8000}

celery -A authentication_service worker -l info
python manage.py migrate --noinput
python manage.py runserver $ADDRESS_VALUE
