# SearchTool GTK

[![AUR Package](https://img.shields.io/aur/version/searchtool-gtk)](https://aur.archlinux.org/packages/searchtool-gtk)

This is a generic GTK search tool and launcher. It runs as a daemon and is activated via either a dmenu-like client or via the UNIX signals SIGRTMIN through SIGRTMAX.

![Screenshot](./screenshot.png)

## Motivation

Similar tools often rely on clunky indexing services or have noticeable startup slowdowns. I decided to implement a simple yet efficient solution - an application that is relatively heavyweight when compared to `dmenu`, but instantaneous to start due to it being run as a hidden window. It is also more related to the `dmenu` category of tools rather than GNOME or KDE launchers because it lists file names rather than trying to index anything.

## Usage

This tool is flexible enough to support a wide variety of use cases. It requires a "Mode" (which implements the [`Mode`](./searchtool_gtk/mode.py) protocol), where the mode determines what items to show, how to filter the items and how to activate them. The list of items is fetched whenever the mode is activated, the list is only repopulated if the item list has changed.

Each mode is determined by a fully qualified Python class name, so creating a custom mode does not require any changes to the tool itself. There following modes are part of the tool:

* [`BinMode`](./searchtool_gtk/modes/bin.py): Lists all binaries in `PATH`
* [`FileMode`](./searchtool_gtk/modes/file.py): Accepts a list of glob patterns and lists all the matching files
* [`ClientMode`](./searchtool_gtk/modes/client.py): Uses UNIX pipes via an auxiliary program, `bin/searchtool-gtk-client` (see below)

Launching the tool is done by simply launching `searchtool-gtk-daemon`.

Make sure that, if launching the daemon via a service manager like systemd, the service is configured not to kill the child processes (`KillMode=process` in systemd).

If a mode is configured to respond to SIGRTMIN+1, then launching the corresponding mode can be done via
```
pkill -SIGRTMIN+1 searchtool-gtk
```

If a mode is configured to work with the client, it will handle the signal itself - simply pass the signal to the client like
```
find | searchtool-gtk-client -SIGRTMIN+1 | cat
```

Once the popup is launched, usage is obvious:

* `Escape` clears any input and hides the popup.
* `Enter` launches the currently selected item.
* `Up/Down` keys, as well as the mouse, allow selecting items.
* Typing simply filters the search results.

The results are sorted by usage. The mode for files (and binaries) uses GTK's recent file history.

## Installation

An [AUR package](https://aur.archlinux.org/packages/searchtool-gtk) is available.

The two hard prerequisites are a supported version of Python and GTK4.

The following steps are sufficient:

* Make use [`poetry`](https://python-poetry.org/) is installed.
* Clone the repository.
* Run `poetry install`.
* Run `pip install [--user] dist/*.whl`
* Make sure `bin/searchtool-gtk-daemon` and `bin/searchtool-gtk-client` can be found in PATH.

If you are packaging this for some other package manager, consider using PEP-517 tools as shown in [this PKGBUILD file](https://aur.archlinux.org/cgit/aur.git/tree/PKGBUILD?h=searchtool-gtk).
