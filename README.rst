=========
Tegenaria
=========

.. image:: https://img.shields.io/travis/andreoliwa/scrapy-tegenaria.svg
        :target: https://travis-ci.org/andreoliwa/scrapy-tegenaria

Scrapy spiders to collect and browse different items (so far, apartment ads).

* Free software: BSD license
* Documentation: https://tegenaria.readthedocs.org.

How to setup the dev environment
--------------------------------

TODO

Metrics
-------

.. image:: https://badge.waffle.io/andreoliwa/scrapy-tegenaria.svg?label=ready&title=Ready
   :alt: Stories in Ready
   :target: http://waffle.io/andreoliwa/scrapy-tegenaria

.. image:: https://graphs.waffle.io/andreoliwa/scrapy-tegenaria/throughput.svg
   :alt: Throughput Graph
   :target: https://waffle.io/andreoliwa/scrapy-tegenaria/metrics

Quickstart
----------

First, set your app's secret key as an environment variable. For example, example add the following to ``.bashrc`` or ``.bash_profile``.

.. code-block:: bash

    export TEGENARIA_SECRET='something-really-secret'


Then run the following commands to bootstrap your environment.


::

    git clone https://github.com/andreoliwa/scrapy-tegenaria
    cd tegenaria
    pip install -r requirements/dev.txt
    flask run

You will see a pretty welcome screen.

Once you have installed your DBMS, run the following to create your app's database tables and perform the initial migration:

::

    flask db init
    flask db migrate
    flask db upgrade
    flask run



Deployment
----------

In your production environment, make sure the ``TEGENARIA_ENV`` environment variable is set to ``"prod"``.


Shell
-----

To open the interactive shell, run ::

    flask shell

By default, you will have access to ``app``, ``db``, and the ``User`` model.


Running Tests
-------------

To run all tests, run ::

    flask test


Migrations
----------

Whenever a database migration needs to be made. Run the following commands:
::

    flask db migrate

This will generate a new migration script. Then run:
::

    flask db upgrade

To apply the migration.

For a full migration command reference, run ``flask db --help``.
