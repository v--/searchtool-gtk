.PHONY: lint

lint:
	poetry run ruff check searchtool_gtk
	poetry run mypy --package searchtool_gtk
