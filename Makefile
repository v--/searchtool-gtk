CC := cc -Wall $(shell pkg-config --cflags --libs gio-2.0)
.DEFAULT_GOAL := build

.PHONY: lint-c lint-python lint build-c build-python build

lint-c:
	clang-tidy src/client/*.c -- $(shell pkg-config --cflags-only-I gio-2.0)

lint-python:
	uv run ruff check
	uv run mypy

lint: lint-c lint-python

dist:
	mkdir dist

dist/searchtool-gtk-%: src/client/%.c | dist
	$(CC) src/client/$*.c -o dist/searchtool-gtk-$*

build-c: dist/searchtool-gtk-activate dist/searchtool-gtk-dmenu

build-python:
	uv build

build: build-c build-python
