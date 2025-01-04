#!/bin/bash
set -e
cd school_project
python manage.py migrate
python manage.py makesuperuser
python manage.py backup_db.py
