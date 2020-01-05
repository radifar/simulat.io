# Simulat.io

in simulat.io folder create postgres directory:

`mkdir postgres`

Then run Postgres docker daemon:

`docker run --name simulat.io-pg -e POSTGRES_PASSWORD=docker -d -p 5432:5432 -v ${PWD}/postgres:/var/lib/postgresql/data postgres:12.0-alpine`