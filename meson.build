project(
    'searchtool-gtk',
    'c',
    version: run_command(['python', '-c', 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])'], check: true).stdout().strip()
)

executable(
  'searchtool-gtk-activate',
  sources: ['src/client/activate.c'],
  dependencies: [dependency('gio-2.0')],
  install: true,
)

executable(
  'searchtool-gtk-dmenu',
  sources: ['src/client/dmenu.c'],
  dependencies: [dependency('gio-2.0')],
  install: true,
)
