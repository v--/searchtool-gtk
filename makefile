.PHONY: lint

lint:
	poetry run ruff check searchtool_gtk bin/searchtool-gtk-daemon
	poetry run mypy --package searchtool_gtk
	poetry run mypy bin/searchtool-gtk-daemon
