# Sherpa

[![Requirements Status](https://requires.io/github/Turistforeningen/sherpa/requirements.svg?branch=master)](https://requires.io/github/Turistforeningen/sherpa/requirements/?branch=master)

The django-based website and CMS for the Norwegian Trekking Association (DNT).

## Requirements

* Docker
* Docker Compose

## Configurations

Sherpa configurations are controlled by the `DJANGO_CONFIGURATION` environment
variable. It defaults to `prod`, but can also be set to `dev` or `staging`.

```
.
|-- private-data
|   `-- conf
|       |-- prod.py
|       |-- staging.py
|       `-- dev.py
`-- sherpa
    |-- settings.py
    `-- conf
        |-- prod.py
        |-- dev.py
        `-- private.py
```

Most of the configurations resides in the public configuration files inside the
`/sherpa/conf/` directory. Only the secret parts should be put inside the
`/private-data/conf/` directory. `settings.py` is responsible for loading the
corresponding configuration files according to the `DJANGO_CONFIGURATION`
environment variable.

### Prod

This is how Sherpa actually should be. The `prod` configuration is always loaded
and `staging` and `dev` overrides what they need to alter.

### Staging

This configuration is, as the name suggest, used when staging feature branches
before merging them into master. This configuration should only have two kinds
of changes compared to `prod`:

1. New, or altered, configurations which will upstreamed to `prod` when merged
   with master.
2. External services which has a testing/sandboxed "version" available (image
   uploads, payment providers etc.) to prevent irreversible actions when
   testing.

### Dev

This configuration is used when running Sherpa locally. It sets `DEBUG` to
`True` and reloads `Gunicorn` when source files are modified.

### Local overrides

While testing locally there may be necessary to override some configurations
locally. This should not be done by editing the existing configuration files
unless they should be committed. Rather they should be put in
`sherpa/conf/private.py` which are you local configuration overrides.

## Install

```
git clone git@github.com:Turistforeningen/sherpa.git
cd sherpa
git submodule init
git submodule update
```

**Build Docker Containers**

```
docker-compose pull
docker-compose build
```

**Import database**

```
docker-compose run --rm psql ./import-prod.sh
```

**Build static files**

```
docker-compose run --rm builder grunt compile
```

## Run on Docker PaaS

`@TODO` some works on Docker PaaS

**Update `/etc/hosts`**

```
echo '172.17.8.102    sherpa.app.dnt.privat' > sudo /etc/hosts
```

**Add `source` remote**

```
cd apps/sherpa
git remote git remote add source https://github.com/Turistforeningen/sherpa.git
```

**Update domain**

```
docker-compose run --rm sherpa python2 manage.py sitedomain www.dnt.no sherpa.app.dnt.privat
```

