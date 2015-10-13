help:
	@echo "fix-isort - fix import order with isort"
	@echo "lint - check style with isort, flake8, pep257 and pylint"
	@echo "lt - lint and test"
	@echo "test - run tests quickly with the default Python"

fix-isort:
	isort --recursive --settings-path . *.py tegenaria_web migrations tests scrapy/tegenaria scrapy/tests

lint:
	isort --recursive --settings-path . --check *.py tegenaria_web migrations tests scrapy/tegenaria scrapy/tests
	flake8 tegenaria_web migrations tests scrapy/tegenaria scrapy/tests
	pep257 tegenaria_web migrations tests scrapy/tegenaria scrapy/tests
	pylint --rcfile=.pylintrc tegenaria_web migrations tests

lt: lint test

test:
	./manage.py test
