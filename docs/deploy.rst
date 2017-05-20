Deployment guide
=================


Docker setup
************

Docker is the recommended deployment mean as it's both easier to setup and upgrade.

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

Non-docker setup
*********************

If you want to setup Trax directly on the system without using Docker, it is still possible but it will require more work.

In this part, we will assume all Trax files will be stored under ``/srv/trax/``. Update the commands accordingly if you plan to use another path.

To run Trax, you will some external services for which installation is not covered here:

- A Redis server
- A PostgreSQL database server

These services can be installed on the same system as Trax application server or somewhere else (in such a case, they will need to be reachable from the Trax applicaiton server).

Cloning the project
-------------------

.. code-block:: shell

    cd /srv
    git clone https://github.com/EliotBerriot/trax.git
    cd trax

Install OS dependencies
-----------------------

Trax require few OS-level dependencies that are listed, for debian systems, under requirements/requirements.apt. If you're on another OS, you'll have to find corresponding packages from your package manager.

Install those packages:

.. code-block:: shell

    sudo xargs -a requirements/requirements.apt apt-get install

Install Python dependencies
----------------------------

Trax is tested under Python 3, more specifically Python 3.5 but it should work the same under older version of Python 3.

.. code-block:: shell

    # create a virtualenv to avoid polluting your system with Trax dependencies
    virtualenv -p `which python3` virtualenv

    # activate the virtualenvironment to ensure further commands are executed
    # there
    source virtualenv/bin/activate

    # install dependencies
    pip install -r requiremends/production/txt

Set project environment variables
----------------------------------

Trax configuration is handled using environment variables.

.. code-block:: shell

    # copy the example environment file
    cp env.example .env

    # Edit the .env file
    nano .env

You'll have to tweak at least the following variables:

- DJANGO_ALLOWED_HOSTS
- DJANGO_SECRET_KEY
- TIME_ZONE
- DATABASE_URL
- REDIS_URL

For each one, please refer to the comments in the .env file itself to understand what value you should provide.


Setup the database
------------------

Assuming your PostgreSQL server is up and running, and you configured the ``DATABASE_URL`` correctly in the previous step, you can now populate the database with initial tables and data:

.. code-block:: shell

    python manage.py migrate

(you will need the database to be created before you can call this command)

Generate static files
---------------------

This is required to collect images, javascript and CSS used by Trax:

.. code-block:: shell

    python manage.py collectstatic

Create an administrator
-----------------------

This is required if you want to log in to Trax admin interface:

.. code-block:: shell

    python manage.py createsuperuser

Check the application server runs properly
------------------------------------------

You should now be able to launch the application server:

.. code-block:: shell

    gunicorn config.wsgi -b 127.0.0.1:8001

This would bind the server on 127.0.0.1 and port. Feel free to tweak that.

Daemonize Trax
---------------

Usually, you'll want to daemonize Trax process to avoid launching them by hand.

This can be done in various way, with tools such as Supervisor or Systemd. This example use two systemd configuration files.

Application server file:

.. code-block:: shell

    # /etc/systemd/system/trax-web.service
    [Unit]
    Description=Trax application server
    After=network.target

    [Service]
    WorkingDirectory=/srv/trax
    ExecStart=/srv/trax/virtualenv/bin/gunicorn config.wsgi -b 127.0.0.1:8001

    [Install]
    WantedBy=multi-user.target

Worker file:

.. code-block:: shell

    # /etc/systemd/system/trax-worker.service
    [Unit]
    Description=Trax worker
    After=network.target

    [Service]
    WorkingDirectory=/srv/trax
    ExecStart=/srv/trax/virtualenv/bin/python manage.py trax_schedule

    [Install]
    WantedBy=multi-user.target

After that, you should enable the files and start the processes:

.. code-block:: shell

    systemctl enable trax-web trax-worker
    systemctl start trax-web trax-worker

And double check everything is working:

.. code-block:: shell

    systemctl status trax-web trax-worker

Set up a reverse proxy
-----------------------

I strongly recommand proxying incoming requests through Nginx or Apache2 instead of making the application server
directly reachable over the internet. This is also the best way to setup HTTPS on Trax.

Example nginx configuration:

.. code-block:: shell

    # /etc/nginx/conf.d/trax.conf
    server {
      listen 80;
      charset     utf-8;
      server_name yourtraxdomain.com;

      location / {
        # checks for static file, if not found proxy to app
        try_files $uri @proxy_to_app;
      }

      # cookiecutter-django app
      location @proxy_to_app {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;

        # update this depending of the adress/port used in your setup
        proxy_pass   http://127.0.0.1:8001;
      }
    }

Remember to restart your nginx instance to load this new configuration:

.. code-block:: shell

    service nginx restart


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
