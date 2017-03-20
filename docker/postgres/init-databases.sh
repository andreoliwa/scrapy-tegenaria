#!/usr/bin/env bash
set -e

# Create dev and test databases during initialisation.
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE tegenaria_dev;
    GRANT ALL PRIVILEGES ON DATABASE tegenaria_dev TO tegenaria;

    CREATE DATABASE tegenaria_test;
    GRANT ALL PRIVILEGES ON DATABASE tegenaria_test TO tegenaria;
EOSQL
