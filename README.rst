trax
====

Simple time tracking server designed to work with Mattermost / Slack

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django

.. image:: ./docs/trax.gif

:License: MIT

Deployment
----------

Deployment is supported using Docker and docker-compose exclusively::

    git clone https://github.com/EliotBerriot/trax.git
    cd trax

    cp env.example .env
    # edit the .env file, especially the SLASH_COMMAND_TOKEN variable
    # and the DJANGO_ALLOWED_HOSTS one
    nano .env

    cp docker-compose.example.yml docker-compose.yml
    # customize any configuration in the docker compose file
    nano docker-compose.yml

    docker-compose build
    docker-compose up -d

    # create tables in the database
    docker-compose run django python manage.py migrate

After that, your trax instance should be available at ``http://yourip/``. The URL to use
for the slash command configuration is ``http://hourip/trax/slash``

You can use the docker-compose.override.example.yml file to tweak the containers behaviour (after renaming it to
docker-compose.override.yml).
