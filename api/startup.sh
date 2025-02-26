#!/bin/bash
cd /home/site/wwwroot
gunicorn --config=gunicorn.conf.py main:app