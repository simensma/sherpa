# Sherpa

[![Requirements Status](https://requires.io/github/Turistforeningen/sherpa/requirements.svg?branch=master)](https://requires.io/github/Turistforeningen/sherpa/requirements/?branch=master)

The django-based website and CMS for the Norwegian Trekking Association (DNT).

## Requirements

* Docker
* Docker Compose

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
docker-compose run --rm builder grunt build
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

