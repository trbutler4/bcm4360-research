.PHONY: check test

check:
	python3 -B tools/check_repository.py

test:
	python3 -B -m unittest discover -s tests -v
