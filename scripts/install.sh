#!/bin/sh
set -eu
case "${1:-}" in
  ''|--autostart) ;;
  *) echo 'Usage: ./scripts/install.sh [--autostart]' >&2; exit 2 ;;
esac
[ "$#" -le 1 ] || { echo 'Too many arguments' >&2; exit 2; }
[ "$(uname -s)" = Linux ] && [ -f /etc/debian_version ] && command -v apt-get >/dev/null || {
  echo 'Install requires Debian/Raspberry Pi OS Desktop Linux.' >&2; exit 1;
}
[ "$(id -u)" -ne 0 ] || { echo 'Run as your desktop user, not root or sudo.' >&2; exit 1; }
command -v sudo >/dev/null || { echo 'sudo is required to install apt packages.' >&2; exit 1; }
sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip mpv libreoffice-impress poppler-utils
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else "Python 3.11+ required")'
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$script_dir/manage_install.py" install "$@"
