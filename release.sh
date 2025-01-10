#!/bin/bash
set -e
cd school_project
python manage.py migrate
python manage.py makesuperuser
python manage.py backup_db
<<<<<<< HEAD
=======
python manage.py clearsessions
>>>>>>> 7008922258437ad93111c3ffd7c2e56094accd98
