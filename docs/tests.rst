Running the test suite
======================

To run tests, assuming you have docker and docker-compose installed, you just need to run:

.. code-block:: shell

    docker-compose -f dev.yml run django pytest

Internally Pytest is used to run tests, meaning you can pass any regular pytest argument, such as ``--ff`` to rerun failures first, or ``-x`` to stop on first failure:

.. code-block:: shell

    docker-compose -f dev.yml run django pytest -x --ff
