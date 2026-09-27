#!/bin/sh
set -eu
case "${1:-}" in
  ''|--purge) ;;
  *) echo 'Usage: ./scripts/uninstall.sh [--purge]' >&2; exit 2 ;;
esac
[ "$#" -le 1 ] || { echo 'Too many arguments' >&2; exit 2; }
[ "$(id -u)" -ne 0 ] || { echo 'Run as your desktop user, not root or sudo.' >&2; exit 1; }
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$script_dir/manage_install.py" uninstall "$@"
