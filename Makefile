#
#	Makefile for Psyche1.
#
#	This Makefile is the human-facing driver.
#	Each rule calls the appropriate tool instead of reimplementing work:
#		all:      the project's primary published artifact
#		build:    sh scripts/site-build.sh
#		site:     sh scripts/site-build.sh + sh scripts/site-condense.sh
#		          (the standard page set; see prompts/features/02-project-pages.md)
#		state:    sh scripts/site-state-fetch.sh (refresh the live state file;
#		          run on the owning host)
#		status:   sh scripts/status.sh (one-screen orientation)
#		check:    the publish sanitization gate over site.out/
#		release:  sh scripts/release-package.sh
#		test:     npm test -> the shell check suite (includes the tool-gated
#		          Python tests)
#		test-python: sh tests/13-python-tests.sh
#		install:  create .venv and install requirements.txt
#		run:      launch the desktop application
#		clean:    remove generated output and Python caches
#		deploy:   RETIRED - publishing goes through the homelab project
#		          (homelab-publish; see the homelab's
#		          documents/09-project-pages-conventions.md).
#

all: build

build:
	sh scripts/site-build.sh

site:
	sh scripts/site-build.sh
	sh scripts/site-condense.sh

state:
	sh scripts/site-state-fetch.sh

status:
	sh scripts/status.sh

check:
	@if [ -d site.out ]; then sh scripts/leak-gate.sh site.out; else echo '==== nothing to check: site.out/ is not built (run make site)'; fi

release:
	sh scripts/release-package.sh

clean:
	rm -rf dataflow.out/* site.out/* logs/*
	find . -path ./.venv -prune -o -type d -name "__pycache__" -print0 | xargs -0 -r rm -rf
	find . -path ./.venv -prune -o -type f -name "*.pyc" -print0 | xargs -0 -r rm -f
	rm -rf .pytest_cache .tox build dist

test:
	npm test

test-python:
	sh tests/13-python-tests.sh

.venv:
	python3 -m venv .venv

install: .venv
	. .venv/bin/activate && pip install -r requirements.txt

run: .venv
	. .venv/bin/activate && python3 -m sources.main

format:
	black sources/

lint:
	flake8 sources/ --max-line-length=100

deploy:
	@echo '==== RETIRED: publishing goes through the homelab project (homelab-publish).'
	@echo '==== Build the pages here (make site / make state), then run the homelab'"'"'s "make deploy"'
	@echo '==== to publish (see homelab documents/09-project-pages-conventions.md).'

.PHONY: all build site state status check release clean test test-python install run format lint deploy
