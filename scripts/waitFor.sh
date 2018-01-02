#!/bin/bash

# TODO: Once postgres installation in container is fixed this can be
# re-enabled.

#dpkg: error processing package postgresql-client-9.4 (--configure):
# subprocess installed post-installation script returned error exit status 2
# Processing triggers for libc-bin (2.19-18+deb8u10) ...
# Processing triggers for systemd (215-17+deb8u7) ...
# Errors were encountered while processing:
#  postgresql-client-9.4
#  E: Sub-process /usr/bin/dpkg returned an error code (1)


# Basic poller to check if the postgres service is available. Has dependency on
# psql being available.

# At this stage it uses the Docker docs example script:
# https://docs.docker.com/compose/startup-order/
#until psql -h "$DB_HOST" -U "postgres" -c '\q'; do
#    >&2 echo "Postgres is unavailable - sleeping"
#    sleep 1
#done

exec "$@"
