PYTHON ?= python3

.PHONY: check validate test compile

validate:
	$(PYTHON) scripts/validate_skill.py

test:
	$(PYTHON) -m unittest discover -s tests -v

compile:
	$(PYTHON) -m compileall -q scripts tests

check: validate compile test
