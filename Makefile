CC := cc -Wall $(shell pkg-config --cflags --libs gio-2.0)

.PHONY: lint-c lint-python lint

lint-c:
	clang-tidy bin_src/*.c -- $(shell pkg-config --cflags-only-I gio-2.0)

lint-python:
	poetry run ruff check searchtool_gtk
	poetry run mypy --package searchtool_gtk

lint: lint-c lint-python

bin/searchtool-gtk-activate: bin_src/activate.c
	$(CC) bin_src/activate.c -o bin/searchtool-gtk-activate

bin/searchtool-gtk-dmenu: bin_src/dmenu.c
	$(CC) bin_src/dmenu.c -o bin/searchtool-gtk-dmenu
