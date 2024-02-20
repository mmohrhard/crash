# Current LibreOffice crash reporting server

Accepts crash reports from a LibreOffice instance, processes it and displays the information on a website. Additionally contains a number of helper tools around the crash reporting.

## Developers

The server uses django and requires at least django 1.9 with uwsgi and uses environment variables for configuration.

A local setup requires configuration variables set according to the local setup. After that a minimal setup with some initial data can be created with `./manage.py setup`. A minimal version should be available through `./manage.py runserver`.

### Run locally

It requires python 2.7.

You can install `pyenv` to manage multiple python versions. Instructions here: https://realpython.com/intro-to-pyenv/#installing-pyenv

```
pyenv install -v 2.7
```

Install virtualenv to create a virtual environment and isolate the dependecies of this project.

```
python -m pip install virtualenv
python -m virtualenv venv
source venv/bin/activate
```

Install the prerequisites to install psycopg2 https://www.psycopg.org/docs/install.html#build-prerequisites

Run to install dependencies:
```
python -m pip install -r requirements.txt
```

Edit ph_hba.conf (it might be located in /var/lib/pgsql/data/pg_hba.conf) change

```
# IPv4 local connections:
host    all              all             127.0.0.1/32             ident
# IPv6 local connections:
host    all              all             ::1/128                  ident
```

ident to md5

```
# IPv4 local connections:
host    all              all             127.0.0.1/32             md5
# IPv6 local connections:
host    all              all             ::1/128                  md5
```

Execute

```
cd django/crashreport
python manage.py migrate
mkdir /tmp/{upload_dir,symbols,static}
python manage.py setup
```

Change settings files from

```
-STATIC_ROOT = os.environ.get('STATIC_ROOT', '/srv/www/static')
```

To

```
+STATIC_ROOT = os.environ.get('STATIC_ROOT', '/tmp/static')
```

Run the local server with

```
python manage.py runserver
```

#### Troubleshooting

If you receive an error on `import psycopg2` try installing `libxcrypt-compat`.

## Production

The production instance can be found at [crashreport.libreoffice.org](http://crashreport.libreoffice.org).
