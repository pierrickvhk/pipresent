"""Deterministic mounted-media discovery and transactional local imports."""

import getpass
import json
import logging
import os
import shutil
import tempfile
import time
import uuid
from pathlib import Path

from pipresent.config import SUPPORTED, Config, PiPresentError, select_content
from pipresent.paths import AppPaths


def usb_candidates(root: Path) -> list[Path]:
    if not root.exists():
        return []
    candidates = []
    for mount in sorted(root.iterdir()):
        if mount.is_symlink() or not mount.is_dir():
            continue
        if (mount / "presentation.json").exists() or any(
            p.suffix.lower() in SUPPORTED for p in mount.iterdir()
        ):
            candidates.append(mount)
    return candidates


def discover_usb(root: Path, wait: float = 7.0) -> Path | None:
    logging.info("USB discovery: %s (wait up to %.1fs)", root, wait)
    deadline = time.monotonic() + wait
    while True:
        candidates = usb_candidates(root)
        if len(candidates) > 1:
            raise PiPresentError(
                "Multiple potential USB sources; leave only one presentation drive"
            )
        if candidates:
            logging.info("USB detected: %s", candidates[0])
            return candidates[0]
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return None
        time.sleep(min(0.25, remaining))


def load_cached(paths: AppPaths) -> tuple[Path, Config]:
    try:
        name = (paths.data / "current").read_text(encoding="utf-8").strip()
        if len(name) != 32 or any(c not in "0123456789abcdef" for c in name):
            raise PiPresentError("Invalid cache pointer")
        return select_content(paths.data / "imports" / name)
    except OSError as exc:
        raise PiPresentError(
            "No usable cached presentation; insert a configured USB drive"
        ) from exc


def import_content(source: Path, paths: AppPaths) -> tuple[Path, Config]:
    media, config = select_content(source)
    paths.ensure()
    imports = paths.data / "imports"
    imports.mkdir(exist_ok=True)
    generation = uuid.uuid4().hex
    target = imports / generation
    pointer: Path | None = None
    try:
        with tempfile.TemporaryDirectory(prefix=".staging-", dir=imports) as staging:
            stage = Path(staging)
            before = media.stat()
            copied = stage / media.name
            shutil.copyfile(media, copied)
            after = media.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                raise PiPresentError("USB content changed during import; retry with a stable file")
            if copied.stat().st_size != before.st_size:
                raise PiPresentError("Incomplete USB copy; previous cache retained")
            (stage / "presentation.json").write_text(
                json.dumps({"content": media.name, "slide_duration": config.slide_duration}),
                encoding="utf-8",
            )
            select_content(stage)
            for item in stage.iterdir():
                with item.open("rb") as handle:
                    os.fsync(handle.fileno())
            stage.rename(target)
        pointer = paths.data / f".current-{generation}"
        with pointer.open("w", encoding="utf-8") as handle:
            handle.write(generation + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        pointer.replace(paths.data / "current")
    except BaseException:
        # The active generation is never touched until the atomic pointer replacement.
        shutil.rmtree(target, ignore_errors=True)
        if pointer is not None:
            pointer.unlink(missing_ok=True)
        raise
    logging.info("Content imported locally: %s", target / media.name)
    return target / media.name, Config(media.name, config.slide_duration)


def acquire(paths: AppPaths, root: Path | None = None, wait: float = 7.0) -> tuple[Path, Config]:
    source = discover_usb(root if root is not None else Path("/media") / getpass.getuser(), wait)
    if source is not None:
        # An explicit but invalid source fails loudly, rather than playing something unexpected.
        return import_content(source, paths)
    logging.info("No USB presentation found; cache fallback")
    return load_cached(paths)
