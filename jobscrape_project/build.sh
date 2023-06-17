#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

gunicorn --worker-tmp-dir /dev/shm jobscrape_project.wsgi