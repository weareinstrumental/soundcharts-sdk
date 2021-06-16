SHELL := /bin/bash
aws_region=eu-west-2
stage=dev
operation=patch
test_pattern="*"

.PHONY: update-deps init update install

init:
	# Run this first
	@echo "Setting up dependencies"; \
	python3 -m venv venv; \
	source venv/bin/activate; \
	pip install pip-tools

update-deps:
	python3 -m venv venv; \
	source venv/bin/activate; \
	pip install --upgrade pip; \
	pip-compile --upgrade --output-file dev-requirements.txt dev-requirements.in && \
	pip-compile --upgrade --output-file requirements.txt requirements.in && \
	pip install --upgrade -r requirements.txt -r dev-requirements.txt -r tests/requirements.txt

install:
	source venv/bin/activate && \
	pip install --editable .

init-package: init update-deps install
	@echo "Initialising package" && \
	git tag v1.0.0 -m "First version" && \
	git push origin v1.0.0

unit-tests:
	@source venv/bin/activate && \
	coverage run --source src/ tests/run.py $(test_pattern) && \
	coverage html --include=src/* && \
	echo "" && \
	echo "To view coverage report, run 'open htmlcov/index.html'"

release:
	@git diff-index --quiet HEAD -- || (printf "\nPlease commit/stash all changes before release\n"; exit 1)
	@git diff-index --quiet origin/`git branch | grep \* | cut -d ' ' -f2` -- || (printf "\nPlease push all changes to include them in releease\n"; exit 1)

	$(eval current_version = $(shell git tag --sort=-v:refname | head -1))
	$(eval version = $(shell bin/increment_version.py "${current_version}" ${operation}))
	@echo "Tagging release" ${version} && \
	sed -i.bak "s/\"version\": \".*\"/\"version\": \"${version}\"/g" package.json && \
	sed -i.bak "s/version=\".*\"/version=\"${version}\"/g" setup.py && \
	git add package.json setup.py && \
	git commit -m "Update version to ${version}" && \
	git push && \
	git tag v${version} -m "${message}"
	git push origin v${version}