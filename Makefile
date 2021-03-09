SHELL := /usr/bin/env bash

.PHONY: unit
unit:
	poetry run pytest -v \
		-vv \
		--cov=browser_fetcher \
		--capture=no \
		--cov-report=term-missing \
 		--cov-config=.coveragerc \

.PHONY: mypy
mypy:
	poetry run mypy browser_fetcher

.PHONY: lint
lint:
	poetry run pylint browser_fetcher

test: unit
