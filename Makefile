PYTHON ?= python3

.PHONY: check validate eval-validate test compile package-check release-check package clean

validate:
	$(PYTHON) scripts/validate_skill.py

eval-validate:
	$(PYTHON) scripts/run_evals.py --validate-only

test:
	$(PYTHON) -m unittest discover -s tests -v

compile:
	$(PYTHON) -m compileall -q scripts tests

package-check:
	$(PYTHON) scripts/package_skill.py --check

release-check:
	$(PYTHON) scripts/release_check.py

package:
	$(PYTHON) scripts/package_skill.py --output-dir dist

clean:
	rm -rf dist
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

check: validate eval-validate compile test package-check release-check
