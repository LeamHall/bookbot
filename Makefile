# Makefile

SHELL = /usr/bin/bash

.PHONY:test
test:
	python -m unittest

clean:
	find . -type f -name "*.pyc" -exec rm {} \;
	find . -type f -name "*.swp" -exec rm {} \;

all: clean test
	python -m black -l79 .
	coverage run -m unittest
	coverage report -m 
	-flake8

