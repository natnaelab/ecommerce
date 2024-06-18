#!/bin/sh
python manage.py migrate
gunicorn ecommerce.wsgi:application --bind 0.0.0.0:8000