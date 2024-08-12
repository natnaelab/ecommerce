#!/bin/sh
export DJANGO_SETTINGS_MODULE=ecommerce.settings.prod
python manage.py migrate
gunicorn ecommerce.wsgi:application --bind 0.0.0.0:8000