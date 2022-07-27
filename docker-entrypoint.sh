#!/bin/sh
python manage.py makemigrations || exit 1
python manage.py migrate || exit 1
python manage.py createcachetable || exit 1

if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_USERNAME
fi

$@

