SHELL := $(shell which bash)

all: build

clean:
	rm -rf .cache .eggs venv *.out *.xml cov_html .coverage && \
	find . -name '*.pyc' -delete && \
	find . -name '*.egg-info' -type d -exec rm -r "{}" + && \
	find . -name 'dist' -type d -exec rm -r "{}" + && \
	find . -name 'build' -type d -exec rm -r "{}" + && \
	find . -name '__pycache__' -type d -exec rm -r "{}" + && \
	find . -name '.pytest_cache' -type d -exec rm -r "{}" + && \
	pipenv uninstall --all

install-deps:
	pipenv install --skip-lock --sequential

build: clean install-deps
	$(info ===== build =====)
	pipenv run "python setup.py bdist_wheel"

install-deps-tests:
	pipenv install --dev --skip-lock --sequential

build-dev: install-deps-tests

lint: build-dev
	$(info ===== lint =====)
	pipenv run flake8 .

test: build-dev
	$(info ===== test =====)
	pipenv run pytest -c pytest.ini -s --junitxml=./test-report.xml --cov=estop --cov-append ./tests/ --cov-report html:./cov_html

tests: lint test

unit-tests: test

view-cov:
ifeq ($(shell uname -s),Darwin)
	open cov_html/index.html
else
	xdg-open cov_html/index.html
endif

publish:
	$(info ===== publish =====)
ifndef REPOSITORY_URL
	$(error REPOSITORY_URL is not set)
endif
ifndef REPOSITORY_USERNAME
	$(error REPOSITORY_USERNAME is not set)
endif
ifndef REPOSITORY_PASSWORD
	$(error REPOSITORY_PASSWORD is not set)
endif
	TWINE_REPOSITORY_URL=$(REPOSITORY_URL) \
	TWINE_USERNAME=$(REPOSITORY_USERNAME) \
	TWINE_PASSWORD=$(REPOSITORY_PASSWORD) \
	pipenv run "twine upload dist/*"

.PHONY: all clean build tests unit-tests publish
