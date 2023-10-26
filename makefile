.PHONY: lint

lint:
	poetry run ruff check searchtool_gtk
	poetry run mypy --package searchtool_gtk

bin/searchtool-gtk-activate: source/activate.d
	dub build --build=release :activate

bin/searchtool-gtk-dmenu: source/dmenu.d
	dub build --build=release :dmenu
