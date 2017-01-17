Deployment guide
=================

Deployment is supported using Docker and docker-compose exclusively:

.. code-block:: shell

    # clone the repository
    git clone https://github.com/EliotBerriot/trax.git
    cd trax

    # setup the environment variables
    # edit the .env file, especially the TIME_ZONE variable
    # and the DJANGO_ALLOWED_HOSTS one
    cp env.example .env
    nano .env

    # set up the docker-compose file
    # customize any configuration in the docker compose file
    # especially, you can change the listening port and ip
    cp docker-compose.example.yml docker-compose.yml
    nano docker-compose.yml

    # build and run the containers
    docker-compose build
    docker-compose up -d

    # create tables in the database
    docker-compose run django python manage.py migrate

    # create an admin user (this will be needed to configure your tokens)
    docker-compose run django python manage.py createsuperuser

After that, your trax instance should be available at http://serverip:8079/, unless you customized the port / ip in the docker-compose file.

You can login to the admin interface at http://serverip:8079/, using the credentials provided in the ``createsuperuser`` command.

I strongly suggest you deploy a reverse proxy in front of your trax server, for example with nginx.


Initial configuration
*********************

In this part, we will assume your mattermost server is available at http://mattermost and your trax server at http://trax.

Mattermost configuration
------------------------

Head over your mattermost server so you can setup the trax integration.

In the system console, you will have to enable incoming webhooks and slash commands for the trax integration to work.

After that, you have to configure two integrations:

1. A slash command, pointing to ``http://trax/trax/slash``, so mattermost users can interact with trax using a slash command (I recommand ``trax`` as the trigger word but you can use something else). Copy the validation token, it will be useful
2. (optionnal) an incoming webhook, so that trax can send reminders in mattermost channels. Also copy the webhook URL.

Trax configuration
------------------

Log in with your superuser credentials at http://trax/admin/, and visit the `Global preferences <http://trax/admin/dynamic_preferences/globalpreferencemodel/>`_ section. This is the place where you'll have to input your trax instance settings:

1. ``trax__slash_command_token``: input the validation token you got from the mattermost step
2. ``trax__webhook_url``: input the webhook URL you got from the mattermost step

Final checks
------------

After that, you should be able to interact with trax within mattermost using the trigger word you choosed::

    /trax help

You should see a list of available commands.

You can now head over :doc:`/user-guide`.

Upgrading to a newer version
****************************

Upgrading to a newer version is done as follows:

.. code-block:: shell

    git pull
    git checkout <tag_or_commit>
    docker-compose up -d --build
