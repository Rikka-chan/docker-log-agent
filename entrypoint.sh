#!/usr/bin/env bash

gunicorn server:app -k gevent -b 0.0.0.0:5000 --worker-connections 1000