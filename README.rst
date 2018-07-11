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

