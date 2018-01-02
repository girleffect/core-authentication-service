#!/bin/bash

ADDRESS_VALUE=${ADDRESS:0.0.0.0:800}

python manage.py migrate
python manage.py runserver $ADDRESS_VALUE
