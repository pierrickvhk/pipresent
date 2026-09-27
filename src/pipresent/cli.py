"""Appliance entry point and human-readable diagnostics."""

import argparse
import logging
import math
import os
import shutil
import sys
import tempfile
from logging.handlers import RotatingFileHandler
from pathlib import Path

from pipresent import __version__
from pipresent.config import Config, PiPresentError
from pipresent.loader import acquire, load_cached
from pipresent.paths import AppPaths
from pipresent.router import play


def setup_logging(paths: AppPaths) -> None:
    paths.ensure()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            RotatingFileHandler(
                paths.state / "pipresent.log", maxBytes=2_000_000, backupCount=3, encoding="utf-8"
            ),
        ],
        force=True,
    )


def doctor(paths: AppPaths) -> int:
    failed = False
    print(f"PASS Python {sys.version.split()[0]} (requires 3.11+)")
    for tool, package in (
        ("mpv", "mpv"),
        ("libreoffice", "libreoffice-impress"),
        ("pdftoppm", "poppler-utils"),
    ):
        executable = shutil.which(tool)
        if executable:
            print(f"PASS {tool}: {executable}")
        else:
            print(f"FAIL {tool}: install Debian package {package}")
            failed = True
    for directory in (paths.data, paths.cache, paths.state):
        try:
            directory.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryFile(dir=directory):
                pass
            print(f"PASS Writable directory: {directory}")
        except OSError as exc:
            print(f"FAIL Directory {directory}: {exc}")
            failed = True
    if os.environ.get("WAYLAND_DISPLAY") or os.environ.get("DISPLAY"):
        print("PASS Display environment present (actual display access needs a playback test)")
    else:
        print("WARN No WAYLAND_DISPLAY or DISPLAY; launch inside the graphical desktop session")
    try:
        media, _ = load_cached(paths)
        print(f"PASS Cached content: {media}")
    except (PiPresentError, OSError) as exc:
        print(f"WARN Cached content: {exc}")
    return 1 if failed else 0


def nonnegative(value: str) -> float:
    try:
        result = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a finite nonnegative number") from exc
    if not math.isfinite(result) or result < 0:
        raise argparse.ArgumentTypeError("must be a finite nonnegative number")
    return result


def positive(value: str) -> float:
    result = nonnegative(value)
    if result == 0:
        raise argparse.ArgumentTypeError("must be positive")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="PiPresent: fullscreen presentation player")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    start = commands.add_parser("start", help="Import USB content or play the last local import")
    start.add_argument("--usb-root", type=Path, help="Mount parent (default: /media/current-user)")
    start.add_argument(
        "--wait", type=nonnegative, default=7.0, help="USB wait seconds (default: 7)"
    )
    commands.add_parser("doctor", help="Check dependencies, directories, display and cache")
    manual = commands.add_parser("play", help="Play a specific local file")
    manual.add_argument("path", type=Path)
    manual.add_argument("--slide-duration", type=positive, default=8.0)
    args = parser.parse_args(argv)
    paths = AppPaths.discover()
    if args.command == "doctor":
        return doctor(paths)
    try:
        setup_logging(paths)
        logging.info("PiPresent %s startup", __version__)
        if args.command == "start":
            media, config = acquire(paths, args.usb_root, args.wait)
        else:
            media, config = args.path.resolve(), Config(slide_duration=args.slide_duration)
        play(media, config, paths)
        return 0
    except KeyboardInterrupt:
        logging.info("Playback interrupted")
        return 130
    except (PiPresentError, OSError) as exc:
        logging.error("%s", exc)
        return 1
    except Exception:
        logging.exception("Unexpected failure")
        return 1
