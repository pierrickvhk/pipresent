"""Small, strict USB configuration and media validation."""

import json
import logging
import math
from dataclasses import dataclass
from pathlib import Path

SUPPORTED = frozenset({".pptx", ".pdf", ".mp4", ".mkv", ".mov"})


class PiPresentError(Exception):
    """An actionable application error."""


@dataclass(frozen=True)
class Config:
    content: str | None = None
    slide_duration: float = 8.0


def positive_number(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PiPresentError("slide_duration must be a positive finite number")
    try:
        result = float(value)
    except OverflowError as exc:
        raise PiPresentError("slide_duration is too large") from exc
    if not math.isfinite(result) or result <= 0:
        raise PiPresentError("slide_duration must be a positive finite number")
    return result


def load_config(directory: Path) -> Config:
    path = directory / "presentation.json"
    if not path.exists():
        return Config()
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise PiPresentError(f"Cannot read configuration {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PiPresentError(f"{path}: expected a JSON object")
    content = value.get("content")
    if content is not None and (
        not isinstance(content, str)
        or not content
        or content in {".", ".."}
        or "/" in content
        or "\\" in content
        or "\x00" in content
    ):
        raise PiPresentError("content must be a filename in the USB root, without directories")
    if "content" in value and content is None:
        raise PiPresentError("content must be a filename, not null")
    config = Config(content, positive_number(value.get("slide_duration", 8)))
    logging.info("Configuration loaded: %s", path)
    return config


def validate_media(path: Path) -> Path:
    if path.suffix.lower() not in SUPPORTED:
        raise PiPresentError(f"Unsupported content extension: {path.suffix}")
    if path.is_symlink() or not path.is_file():
        raise PiPresentError(f"Content missing or not a regular non-symlink file: {path}")
    if path.stat().st_size == 0:
        raise PiPresentError(f"Content is empty: {path}")
    logging.info("Content validated: %s", path)
    return path


def select_content(directory: Path) -> tuple[Path, Config]:
    config = load_config(directory)
    if config.content is not None:
        return validate_media(directory / config.content), config
    candidates = sorted(p for p in directory.iterdir() if p.suffix.lower() in SUPPORTED)
    if not candidates:
        raise PiPresentError(f"No supported content in {directory}")
    if len(candidates) != 1:
        raise PiPresentError(
            f"Multiple content files in {directory}; specify content in presentation.json"
        )
    return validate_media(candidates[0]), config
