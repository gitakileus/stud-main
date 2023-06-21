#!/bin/bash

DIR=/var/www/stud

cd ${DIR} && git pull && source stud/bin/activate && pip install -r requirements.txt && python3 manage.py migrate && python3 manage.py collectstatic --noinput

sudo systemctl restart gunicorn.service