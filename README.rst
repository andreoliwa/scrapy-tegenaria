=========
Tegenaria
=========

.. image:: https://img.shields.io/travis/andreoliwa/scrapy-tegenaria.svg
        :target: https://travis-ci.org/andreoliwa/scrapy-tegenaria

.. image:: https://img.shields.io/pypi/v/tegenaria.svg
        :target: https://pypi.python.org/pypi/tegenaria

Scrapy spiders to collect and browse different items (so far, apartment ads).

This repository contains two twin projects:

1. A `Scrapy <https://scrapy.org/>`_ project with spiders to collect different items;
1. A `Flask <http://flask.pocoo.org/>`_ app to browse and manipulate the items that were collected by the spiders.

Scrapy is still using Python 2, while Flask is already on Python 3.
As soon as Scrapy gets a Python 3 version, this can become a single project with two modules.

Flask is the main project, while Scrapy is all contained in a sub directory.
Maybe Git submodules could also be used here; that can be tried later.


* Free software: BSD license
* Documentation: https://tegenaria.readthedocs.org.

How to setup the dev environment
--------------------------------

1. Clone this repo.
1. Create a Python 2 virtual env for the Scrapy project and test it.

::

  cd ~/some/path/scrapy-tegenaria/scrapy
  mkvirtualenv tegenaria-scrapy --python=/usr/bin/python2.7
  pwd > ~/.virtualenvs/tegenaria-scrapy/.project
  cdproject
  pip install -U -r requirements/dev.txt
  scrapy
  deactivate

1. Create a virtual env for the Flask project and test if it's working.

::

  cd ~/some/path/scrapy-tegenaria/
  mkvirtualenv tegenaria
  pwd > ~/.virtualenvs/tegenaria/.project
  cdproject
  pip install -U -r requirements/dev.txt
  ./manage.py server


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
    python manage.py server

You will see a pretty welcome screen.

Once you have installed your DBMS, run the following to create your app's database tables and perform the initial migration:

::

    python manage.py db init
    python manage.py db migrate
    python manage.py db upgrade
    python manage.py server



Deployment
----------

In your production environment, make sure the ``TEGENARIA_ENV`` environment variable is set to ``"prod"``.


Shell
-----

To open the interactive shell, run ::

    python manage.py shell

By default, you will have access to ``app``, ``db``, and the ``User`` model.


Running Tests
-------------

To run all tests, run ::

    python manage.py test


Migrations
----------

Whenever a database migration needs to be made. Run the following commands:
::

    python manage.py db migrate

This will generate a new migration script. Then run:
::

    python manage.py db upgrade

To apply the migration.

For a full migration command reference, run ``python manage.py db --help``.
