.PHONY: setup
setup:
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

# Rather than working out the right dependencies, just rebuild this every time.
# If a human is rebuilding it, it's probably because something has changed.
.PHONY: dist/main
dist/main:
	. venv/bin/activate && pyinstaller --onefile src/main.py
