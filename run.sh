#!/bin/bash
set -e
gunicorn school_project.school_project.wsgi:application --log-file -