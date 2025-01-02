#!/bin/bash
cd school_project
set -e
gunicorn project.wsgi --log-file -
