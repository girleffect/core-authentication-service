#!/bin/bash

# Create an empty database and user that by default has the same
# name as the database and a password of 'password'.
# This script must be run as the postgres user.

DB=${1:?"You must specify a database name"}
DB_USER=${2:-$1}

cat - <<EOF
DROP DATABASE IF EXISTS ${DB};
DROP USER IF EXISTS ${DB_USER};

CREATE DATABASE ${DB}
ENCODING 'UTF8'
TEMPLATE template0;

CREATE USER ${DB_USER} PASSWORD 'password';
GRANT ALL ON DATABASE ${DB} TO ${DB_USER};

\c ${DB};
CREATE EXTENSION pg_trgm;
EOF

