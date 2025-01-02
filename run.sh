#!/bin/bash
set -e
cd school_project
gunicorn wsgi:application --log-file -