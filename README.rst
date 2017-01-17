trax
====

Simple time tracking server designed to work with Mattermost / Slack.

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django

:License: MIT

Overview
--------

Trax is a time tracking server written in Python/Django, designed to work within a chat server such as Mattermost or Slack. You interact with it directly from your chat server, using slash commands and webhooks::

    # start to work on something
    /trax start making coffee

    # Get a pretty reminder in channel in 5 minutes
    /trax remind add "Call mom" "in 5 minutes"

    # start to work on something else
    /trax start reading emails

    # Stop working
    /trax stop

    # see how you spent your time today
    /trax stats

Documentation
-------------

Detailed user guide, installation and deployment instructions are available at https://traxio.readthedocs.io/.
