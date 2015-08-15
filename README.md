# Tegenaria

This repository contains two twin projects:

1. A [Scrapy](http://scrapy.org/) project with spiders to collect different items;
1. A [Flask](http://flask.pocoo.org/) app to browse and manipulate the items that were collected by the spiders.

Scrapy is still using Python 2, while Flask is already on Python 3.
As soon as Scrapy gets a Python 3 version, this can become a single project with two modules.

Maybe Git submodules could also be used here; that can be tried later.

## How to setup the dev environment

1. Clone this repo.
1. Create a Python 2 virtual env for the Scrapy project and test it.
  ```shell
  cd ~/some/path/python-tegenaria/scrapy
  mkvirtualenv tegenaria-scrapy --python=/usr/bin/python2.7
  pwd > ~/.virtualenvs/tegenaria-scrapy/.project
  cdproject
  pip install -U -r requirements/dev.txt
  scrapy
  deactivate
  ```
1. Create a virtual env for the Flask project and test if it's working.
  ```shell
  cd ~/some/path/python-tegenaria/flask
  mkvirtualenv tegenaria-flask
  pwd > ~/.virtualenvs/tegenaria-flask/.project
  cdproject
  pip install -U -r requirements/dev.txt
  ./manage.py server
  ```
