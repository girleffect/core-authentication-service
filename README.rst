core-authentication-service
===========================
.. image:: https://travis-ci.org/girleffect/core-authentication-service.svg?branch=develop
    :target: https://travis-ci.org/girleffect/core-authentication-service

.. image:: https://coveralls.io/repos/github/girleffect/core-authentication-service/badge.svg?branch=develop
     :target: https://coveralls.io/github/girleffect/core-authentication-service?branch=develop

Documentation for this project can be found here:
https://girleffect.github.io/core-authentication-service/

Migration 0001 for otp_totp will break if user AUTH_USER_MODEL is changed after running migrations.

Env vars: CELERY_APP and BUILDER are used to flag the need for certain other env variables.

Notes on how the production system was bootstrapped can be found in `bootstrap.md`.


Env vars:

# Docker base image

# Migrations can no longer be run without a specific env var being set specifically for it.

- SKIP_MIGRATIONS=1

# Django settings

- CELERY_BROKER_URL=redis://redis:6379/2
- REDIS_URI=redis://redis:6379/3
- ALLOWED_HOSTS=*
- STATIC_ROOT=/app/static
- MEDIA_ROOT=/app/media
- EMAIL_HOST=smtp

# Comma delimited, key=val pairs dictionary

- DB_DEFAULT=ENGINE=django.db.backends.postgresql,NAME=authentication_service,USER=authentication_service,PASSWORD=password,HOST=db,PORT=5432

# Not set on QA

- LOG_LEVEL=DEBUG

# API services

- USER_DATA_STORE_API_KEY=demo-authentication-service-api-key
- ACCESS_CONTROL_API_KEY=demo-authentication-service-api-key
- ALLOWED_API_KEYS=demo-management-layer-api-key
- ACCESS_CONTROL_API=http://core-access-control:8080/api/v1
- USER_DATA_STORE_API=http://core-user-data-store:8080/api/v1

# Kinesis related vars

- USE_KINESIS_PRODUCER=true

# If above is true, these are required

# Comma delimited, key=val pairs dictionary

- KINESIS_SESSION=aws_access_key_id=foobar,aws_secret_access_key=foobar,region_name=us-east-1
- KINESIS_PRODUCER=stream_name=test-stream
- KINESIS_BOTO3_CLIENT_SETTINGS=endpoint_url=http://localstack:4568

# The variables below are not used in production, just the docker-compose env

- WAGTAIL_1_CALLBACK=http://wagtail-demo-1-site-1:8000/oidc/callback/
- WAGTAIL_2_CALLBACK=http://wagtail-demo-2-site-1:8000/oidc/callback/
- WAGTAIL_3_CALLBACK=http://wagtail-demo-1-site-2:8000/oidc/callback/
- WAGTAIL_1_LOGOUT_REDIRECT=http://wagtail-demo-1-site-1:8000/
- WAGTAIL_2_LOGOUT_REDIRECT=http://wagtail-demo-2-site-1:8000/
- WAGTAIL_3_LOGOUT_REDIRECT=http://wagtail-demo-1-site-2:8000/
