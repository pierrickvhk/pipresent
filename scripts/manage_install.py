"""Installer internals: preserve unrelated configuration and require ownership markers."""

import argparse
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

BEGIN = "# PiPresent BEGIN"
END = "# PiPresent END"
MARKER = "# Managed by PiPresent installer"


def xdg(name: str, default: str) -> Path:
    value = Path(os.environ.get(name, str(Path.home() / default)))
    return value if value.is_absolute() else Path.home() / default


def without_block(text: str) -> str:
    lines = text.splitlines(keepends=True)
    starts = [i for i, line in enumerate(lines) if line.strip() == BEGIN]
    ends = [i for i, line in enumerate(lines) if line.strip() == END]
    if not starts and not ends:
        return text
    if len(starts) != 1 or len(ends) != 1 or starts[0] >= ends[0]:
        raise RuntimeError("Malformed PiPresent autostart markers; repair the file manually")
    return "".join(lines[: starts[0]] + lines[ends[0] + 1 :])


def atomic_write(path: Path, text: str, mode: int = 0o644) -> None:
    if path.is_symlink():
        raise RuntimeError(f"Refusing to overwrite a symlink: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, delete=False
    ) as f:
        temporary = Path(f.name)
        try:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
            temporary.chmod(mode)
            temporary.replace(path)
        finally:
            temporary.unlink(missing_ok=True)


def update_autostart(path: Path, launcher: Path, log: Path, enable: bool) -> None:
    if path.is_symlink():
        raise RuntimeError(f"Refusing to edit symlinked autostart: {path}")
    original = path.read_text(encoding="utf-8") if path.exists() else ""
    text = without_block(original)
    if enable:
        if text and not text.endswith("\n"):
            text += "\n"
        command = f"{shlex.quote(str(launcher))} start >> {shlex.quote(str(log))} 2>&1 &"
        text += f"{BEGIN}\n{command}\n{END}\n"
    if text != original:
        # A backup of the original precedes the first actual edit.
        backup = path.with_name(path.name + ".pipresent.bak")
        if path.exists() and not backup.exists():
            atomic_write(backup, original, path.stat().st_mode & 0o777)
        atomic_write(path, text, path.stat().st_mode & 0o777 if path.exists() else 0o644)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["install", "uninstall"])
    parser.add_argument("--autostart", action="store_true")
    parser.add_argument("--purge", action="store_true")
    args = parser.parse_args()
    data_base = xdg("XDG_DATA_HOME", ".local/share")
    app = data_base / "pipresent-app"
    marker = app / ".pipresent-owned"
    launcher = Path.home() / ".local/bin/pipresent"
    state = xdg("XDG_STATE_HOME", ".local/state") / "pipresent"
    data = data_base / "pipresent"
    cache = xdg("XDG_CACHE_HOME", ".cache") / "pipresent"
    autostart = xdg("XDG_CONFIG_HOME", ".config") / "labwc/autostart"
    if app.is_symlink() or (app.exists() and not marker.is_file()):
        raise RuntimeError(f"Refusing to change an unowned installation: {app}")
    if launcher.is_symlink() or (
        launcher.exists() and MARKER not in launcher.read_text(encoding="utf-8").splitlines()
    ):
        raise RuntimeError(f"Refusing to change an unrelated launcher: {launcher}")
    if args.action == "install":
        if args.autostart:
            if autostart.is_symlink():
                raise RuntimeError("Refusing to edit symlinked autostart")
            without_block(autostart.read_text(encoding="utf-8") if autostart.exists() else "")
        app.mkdir(parents=True, exist_ok=True)
        marker.write_text("PiPresent installation\n", encoding="utf-8")
        environment = app / "venv"
        venv.EnvBuilder(with_pip=True).create(environment)
        subprocess.run(
            [
                str(environment / "bin/python"),
                "-m",
                "pip",
                "install",
                "--upgrade",
                str(Path(__file__).resolve().parents[1]),
            ],
            check=True,
        )
        for directory in (data, cache, state):
            directory.mkdir(parents=True, exist_ok=True)
        # Capture XDG choices so autostart and interactive use share the same data.
        exports = "".join(
            f"export {name}={shlex.quote(str(value))}\n"
            for name, value in (
                ("XDG_DATA_HOME", data_base),
                ("XDG_CACHE_HOME", cache.parent),
                ("XDG_STATE_HOME", state.parent),
            )
        )
        atomic_write(
            launcher,
            f"#!/bin/sh\n{MARKER}\n{exports}exec "
            f'{shlex.quote(str(environment / "bin/pipresent"))} "$@"\n',
            0o755,
        )
        if args.autostart:
            update_autostart(autostart, launcher, state / "autostart.log", True)
        subprocess.run([str(launcher), "doctor"], check=True)
        print(f"Installed: {launcher}\nRun: {launcher} start")
        print("Optional desktop autostart: ./scripts/install.sh --autostart")
        print("Enable desktop auto-login and disable screen blanking; see README.")
    else:
        if args.purge:
            print(f"Permanently remove PiPresent data, cache and logs:\n{data}\n{cache}\n{state}")
            if input("Type PURGE to confirm: ") != "PURGE":
                print("Cancelled; nothing changed.")
                return 1
        update_autostart(autostart, launcher, state / "autostart.log", False)
        launcher.unlink(missing_ok=True)
        if app.exists():
            shutil.rmtree(app)
        if args.purge:
            for directory in (data, cache, state):
                if directory.is_symlink():
                    raise RuntimeError(f"Refusing to purge symlink: {directory}")
                if directory.exists():
                    shutil.rmtree(directory)
        print(
            "PiPresent uninstalled. Cached presentations retained."
            if not args.purge
            else "PiPresent uninstalled and application data purged."
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Installation error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
