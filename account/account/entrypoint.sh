#!/bin/sh

if [ "$DATABASE" = "mysql" ]
then
    echo "Waiting for MySQL..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "MySQL started."
fi

# flush removes data from database
# python manage.py flush --no-input
python manage.py makemigrations --no-input
python manage.py migrate --no-input
python manage.py collectstatic --no-input

# TODO: logs and staticfiles are owned by root

exec "$@"