.PHONY: help test install clean build

help:		## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

test:		## Run the offline test suite (no API key needed)
	python -m unittest discover -s tests -t . -v

install:	## Editable install (provides the `dev_team` command)
	pip install -e .

build:		## Run the team on a spec: make build ARGS='"Build a URL shortener" --show-work'
	python -m dev_team $(ARGS)

clean:		## Remove caches and build artifacts
	find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	rm -rf *.egg-info build dist .eggs
