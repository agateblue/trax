Install locally
===============

To get a working local copy of the project, the recommended setup involves Docker
and docker-compose.

Assumoing you have both of these tools installed, you should be able to spin
up a local copy of the project (and a test mattermost server to see how it works within the chat):

.. code-block:: shell

    docker-compose -f dev.yml up

This build build and launch the required containers, after that, you can access the mattermost server at http://localhost:8065 and the trax server at http://localhost:8000.

Initial configuration
*********************

Mattermost configuration
------------------------

Once your docker containers are up, you can setup easily a test team and user:

.. code-block:: shell

    # create the team
    docker-compose -f dev.yml exec mattermost ./bin/platform team create --name test --display_name "test"

    # create the user
    docker-compose -f dev.yml exec mattermost ./bin/platform user create --firstname test --system_admin --email test@test --username test --password testtest

    # add the user to the team
    docker-compose -f dev.yml exec mattermost ./bin/platform team add test test

After that, you have to configure two integrations:

1. `A slash command <http://localhost:8065/test/integrations/commands/add>`_ , pointing to ``http://trax:8000/trax/slash``, so mattermost users can interact with trax using a slash command (I recommand ``trax`` as the trigger word but you can use something else). Copy the validation token, it will be useful
2. (optionnal) an `incoming webhook <http://localhost:8065/test/integrations/incoming_webhooks/add>`_, so that trax can send reminders in mattermost channels. Also copy the webhook URL (but replace the domain part with ``mattermost`` and remove the port)

Trax configuration
------------------

To finish the trax server configuration, you'll have to create a superuser:

.. code-block:: shell

    docker-compose -f dev.yml run django python manage.py createsuperuser

Once done, log with your credentials at http://localhost:8000/admin/, and visit the `Global preferences <http://localhost:8000/admin/dynamic_preferences/globalpreferencemodel/>`_ section. This is the place where you'll have to input your trax instance settings:

1. ``trax__slash_command_token``: input the validation token you got from the mattermost step
2. ``trax__webhook_url``: input the webhook URL you got from the mattermost step (replace the ``localhost`` part with ``mattermost``, so the URL will look like ``http://mattermost:8065/hooks/ked7nmu37id4zyii316be15d5o``)

Final checks
------------

After that, you should be able to interact with trax within mattermost using the trigger word you choosed::

    /trax help

You should see a list of available commands, if everything works fine.

You can now head over :doc:`/user-guide`.
