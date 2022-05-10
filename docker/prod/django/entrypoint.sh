#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset


cmd="$@"

function postgres_ready(){
python << END
import sys
import psycopg2
import dj_database_url

config = dj_database_url.config()

connection = {
    'dbname': config['NAME'],
    'user': config['USER'],
    'password': config['PASSWORD'],
    'host': config['HOST'],
    'port': config['PORT']
}

try:
    conn = psycopg2.connect(**connection)
except psycopg2.OperationalError as e:
    print(e)
    sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - continuing..."
exec $cmd
