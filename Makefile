.PHONY: clean-pyc clean-build docs clean

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "isort - fix import order with isort"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "ilt - isort, lint and test"
	@echo "iltd - isort, lint, test and docs"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "release - package and upload a release"
	@echo "dist - package"
	@echo "install - install the package to the active Python's site-packages"

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr docs/_build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

isort:
	isort -rc .

lint:
	./manage.py lint

test:
	py.test --verbose --cov tegenaria
	scrapy check -v

test-all:
	tox

docs:
	rm -f docs/tegenaria.rst
	rm -f docs/modules.rst
	mkdir -p docs/_static
	sphinx-apidoc -o docs/ tegenaria
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	open docs/_build/html/index.html

ilt: isort lint test

iltd: isort lint test docs

coverage:
	py.test --cov=tegenaria --cov-report=term --cov-report=html
	open htmlcov/index.html

release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean
	python setup.py install
