# Makefile

SHELL = /usr/bin/bash

.PHONY:test
test:
	python -m unittest

coverage: test
	coverage run -m unittest
	coverage report -m 

clean:
	find . -type f -name "*.pyc" -exec rm {} \;
	find . -type f -name "*.swp" -exec rm {} \;

all: clean coverage
	python -m black -l 79 .
	-flake8 --ignore E251,E266,W391,W503
	semgrep --config "p/default"

