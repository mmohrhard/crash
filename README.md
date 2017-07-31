# Current LibreOffice crash reporting server

Accepts crash reports from a LibreOffice instance, processes it and displays the information on a website. Additionally contains a number of helper tools around the crash reporting.

## Developers

The server uses django and requires at least django 1.9 with uwsgi and uses environment variables for configuration.

A local setup requires configuration variables set according to the local setup. After that a minimal setup with some initial data can be created with `./manage.py setup`. A minimal version should be available through `./manage.py runserver`.

## Production

The production instance can be found at [crashreport.libreoffice.org](http://crashreport.libreoffice.org).
