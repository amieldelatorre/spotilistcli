.ONESHELL:
SHELL:=/bin/bash

clean:
	rm -rf build dist spotilistcli.spec .venv

full-clean: clean
	rm -rf .cache .env .venv

setup-env:
	python3 -m venv .venv
	source ./.venv/bin/activate
	pip install -r requirements.txt

build: setup-env
	source ./.venv/bin/activate
	pip install pyinstaller
	pyinstaller --hidden-import http.server --hidden-import commands.playlist --add-data=commands:commands --onedir --name spotilistcli app.py
