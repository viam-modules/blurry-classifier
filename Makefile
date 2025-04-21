.PHONY: setup
setup: .installed

# This file gets touched when setup.sh succeeds.
.installed:
	./setup.sh

# Rather than working out the right dependencies, just rebuild this every time.
# If a human is rebuilding it, it's probably because something has changed.
.PHONY: dist/main
dist/archive.tar.gz: .installed
	./build.sh

test:
	PYTHONPATH=./src pytest
lint:
	pylint --disable=C0114,C0115 src/
