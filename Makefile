# This is a quick and dirty Makefile for those of us on rolling release
# distros, who are unable to roll back to python 3.6

all:
	@echo "AVAILABLE COMMANDS:"
	@echo "    patch_release"
	@echo "    minor_release"
	@echo "    major_release"
	@echo "    release"

clean:
	isort -y
	flake8

release:
	changelog-gen
	python setup.py sdist upload -r internal

coverage:
	pytest --cov=changelog_gen
