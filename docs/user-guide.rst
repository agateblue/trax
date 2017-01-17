User guide
==========

Interacting with trax
----------------------

Everytime you want to do something with trax, you'll need to type a slash command in your
chat server. Such commands start with a slash and a trigger word:

.. code-block:: shell

    /echo "Hello world"

In the previous example, the trigger world is "echo".

The trigger word for trax should be "trax", but it is totally possible your administrator has configured
it with another trigger word. For the sake of simplicity, in this guide, we will assume your trigger word is "trax".

Here is an example of a trax command:

.. code-block:: shell

    /trax start working

In this example, "start" is a trax command, and "working" is an argument to this command. For trax, this means ``Start a timer named "working"``. Some trax commands require one or many arguments, while some other don't, or only have optional arguments. For example, you could do: ``/trax help`` to get general help, without providing any argument, or ``/trax help start``, with the ``start`` argument, to get help about the ``start`` command.


To sum it up:

- The slash command a way to tell your chat server "I want to interact with another software" (trax here). It's made of a slash and a trigger word, such as ``/trax``
- The trax command is the word that follows the trigger word and tell trax what you want to do, such as ``stop`` in ``/trax stop``
- The arguments come after the trax command. They may be optional, required or even not needed at all


Getting help
------------

The most basic thing you should be able to do is to get help. This is done with the following command:

.. code-block:: shell

    # get general help
    /trax help

    # get help about the config command
    /trax help config
