#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

python manage.py migrate
exec gunicorn -c config/gunicorn.conf.py config.asgi:application
