CC := cc -Wall
.DEFAULT_GOAL := build

.PHONY: lint build-c build-python build

lint:
	uv run ruff check
	uv run mypy

dist:
	mkdir dist

dist/searchtool-gtk-%: src/client/%.c | dist
	$(CC) src/client/$*.c -o dist/searchtool-gtk-$* $(shell pkg-config --cflags --libs gio-2.0) $(CFLAGS)

build-c: dist/searchtool-gtk-activate dist/searchtool-gtk-dmenu

build-python:
	uv build

build: build-c build-python
