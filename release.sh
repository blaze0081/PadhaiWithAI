#!/bin/bash
cd school_project
set -e
python manage.py migrate
python manage.py makesuperuser
