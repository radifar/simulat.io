# Simulat.io

First install all the requirements:

`pip install -r requirements.txt`

in simulat.io folder create postgres directory:

`mkdir postgres`

Then run Postgres docker daemon:

`docker run --name simulat.io-pg -e POSTGRES_PASSWORD=docker -d -p 5432:5432 -v ${PWD}/postgres:/var/lib/postgresql/data postgres:12.0-alpine`

Check if the apps could run:

`python manage.py runserver`

And check by opening `localhost:8000`

Run migration:

`python manage.py migrate`

Create superuser:

`python manage.py createsuperuser`