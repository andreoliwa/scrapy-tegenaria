help:
	@echo "isort - fix import order with isort"
	@echo "lint - check style with flake8 and pylint"
	@echo "test - run tests quickly with the default Python"
	@echo "ilt - isort, lint and test"
	@exit 1

isort:
	isort -rc .

lint:
	flake8 tegenaria migrations tests scrapy/tegenaria scrapy/tests
	pep257 tegenaria migrations tests scrapy/tegenaria scrapy/tests
	pylint --rcfile=.pylintrc tegenaria migrations tests

# FIXME
#lint:
#	./manage.py lint --pylint

test:
	py.test --verbose --cov tegenaria

ilt: isort lint test
