# postpost [![Build Status](https://travis-ci.com/piterpy-meetup/postpost.svg?branch=develop)](https://travis-ci.com/piterpy-meetup/postpost)

metameta

Service for posting to various social medias from one place

## Quick Start

### Docker-based setup
Prerequisites: docker-compose, `.env` file in the project root

Specify Docker tag (see [list of tags](https://hub.docker.com/r/piterpy/postpost/tags) on DockerHub):

`export TAG=dev`

Start containers:

`docker-compose up -d`

Create superuser:

`docker-compose exec api pipenv run python postpost/manage.py createsuperuser`

### Without Docker
Prerequisites: Python 3.6, `.env` file in the project root, Redis running on port `6379` and PostgreSQL on port `5432`

`pipenv install`

`export PYTHONPATH=/full/path/to/postpost`

Copy environment variables:
`cp .env.template .env`

Add values to the variables in `.env`, if you have any, like so:
`VAR_NAME=6666aaaa`

`pipenv run python manage.py migrate`

`pipenv run python manage.py runserver`

`pipenv run celery -A main worker -B`

Add basic user

`pipenv run python manage.py createsuperuser`

### Usage

Login to [admin interface](http://localhost:8000/admin/oauth2_provider/application/) and create OAuth Application with
these params:

 - User: `1`
 - Client type: `Public`
 - Grant type: `Resource owner password based`
 - Name: e.g. `frontend`

Congrats! Now, there are your [swagger](http://localhost:8000/api/swagger) and [redoc](http://localhost:8000/api/redoc)
