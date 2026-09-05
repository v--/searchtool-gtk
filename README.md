# SearchTool GTK

[![AUR Package](https://img.shields.io/aur/version/searchtool-gtk)](https://aur.archlinux.org/packages/searchtool-gtk)

This is a generic GTK search tool and launcher. It runs as a background server and is activated via [D-Bus](https://www.freedesktop.org/wiki/Software/dbus/) as well as client wrappers provided by the project.

## Table of contents

* [Usage](#usage)
* [Installation](#installation)
* [Configuration](#motivation)
* [Motivation](#motivation)

## Usage

![Screenshot](./screenshots/basic.png)

This tool is flexible enough to support a wide variety of use cases. It is configured via a list of "Modes" ([`SearchToolMode`](./src/searchtool_gtk/modes/base.py)), where the mode determines, with the help of collators ([`SearchToolCollator`](./src/searchtool_gtk/collation/base.py)), what items to show, how to filter the items and how to activate them. The list of items is fetched whenever the mode is activated, the list is only repopulated if the item list has changed.

Each mode is determined by a name and a fully qualified Python class name, so creating a custom mode does not require any changes to the tool itself. The following mode classes are part of the tool:

* [`BinMode`](./src/searchtool_gtk/modes/bin.py): Lists all binaries in `PATH`.
* [`FileMode`](./src/searchtool_gtk/modes/file.py): Accepts a list of glob patterns, lists all the matching files and activates a file via `xdg-open`.
* [`ClipHistMode`](./src/searchtool_gtk/modes/cliphist.py) (exported as `ClipHistStandaloneMode` until the next major version): A mode specifically adapted for [ClipHist](https://github.com/sentriz/cliphist).

Launching the tool is done by simply running `searchtool-gtk-server`.

Given the [default configuration](./default_config.toml), we can launch the "binary" mode as follows:

    searchtool-gtk-activate binary

The modes (re)populate the GTK widgets in the background so that the each run is as fast as GTK allows it to be.

Once the popup is launched, usage is obvious:

* `Escape` clears any input and hides the popup.
* `Enter` launches the currently selected item.
* `Up/Down` keys, as well as the mouse, allow selecting items.
* Typing simply filters the search results.

The mode for files (and binaries) uses GTK's recent file history to sort files by their latest usage date.

## Installation

An easy way to install the two executables (`searchtool-gtk-{server,activate}`) for the current user is via [`pipx`](https://pipx.pypa.io):

    pipx install git+https://github.com/v--/searchtool-gtk

An alternative is to use [`uv`](https://docs.astral.sh/uv/):

    uv tool install searchtool-gtk --from git+https://github.com/v--/searchtool-gtk

The hard prerequisites are a supported version of Python and GTK4.

To shave a hundred-or-so milliseconds from every invocation of `searchtool-gtk-activate`, this project also provides a native counterpart. It can be installed to `$dest/bin` via [Meson](https://mesonbuild.com/):

    meson setup builddir --prefix=$dest
    meson install -C builddir

> [!TIP]
> An [AUR package](https://aur.archlinux.org/packages/searchtool-gtk) is available for reference. If you are packaging this for some other package manager, consider using PEP-517 tools as shown in [this PKGBUILD file](https://aur.archlinux.org/cgit/aur.git/tree/PKGBUILD?h=searchtool-gtk).

## Configuration

We use the [XDG config directories](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html) (the defaults should be `/etc/xdg` or `~/.config`) to search for a directory `searchtool` with a configuration file named `config.toml`. The format should be clear from [`default_config.toml`](./default_config.toml).

## Motivation

Similar tools often rely on clunky indexing services or have noticeable startup slowdowns. I decided to implement a simple yet efficient solution - an application that is relatively heavyweight when compared to `dmenu`, but instantaneous to start due to it being run as a hidden window. It is more related to the `dmenu` category of tools rather than GNOME or KDE launchers because it is based on plain text items.

> [!NOTE]
> The current versions still allows a `dmenu`-compatible workflow, but it had some performance problems when used with GTK, so it is currently deprecated.
