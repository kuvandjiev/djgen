#!/bin/bash
python3 /webapps/djgen/manage.py migrate --no-input && python3 /webapps/djgen/manage.py runserver 0.0.0.0:8000 & celery -A djtest worker -l info
