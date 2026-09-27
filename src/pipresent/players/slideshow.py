"""Numerically ordered, endlessly looping static slides."""

import logging
import re
from pathlib import Path

from pipresent.commands import run_command
from pipresent.config import PiPresentError, positive_number
from pipresent.players import COMMON


def slide_key(path: Path) -> list[tuple[int, int | str]]:
    return [
        (0, int(part)) if part.isdigit() else (1, part.lower())
        for part in re.split(r"(\d+)", path.name)
    ]


def slideshow_command(slides: list[Path], duration: float) -> list[str]:
    if not slides:
        raise PiPresentError("No slides generated")
    duration = positive_number(duration)
    return [
        *COMMON,
        f"--image-display-duration={duration:g}",
        "--loop-playlist=inf",
        "--",
        *(str(path.resolve()) for path in sorted(slides, key=slide_key)),
    ]


def play_slideshow(slides: list[Path], duration: float) -> None:
    logging.info("Slideshow playback start: %d slides, %.2fs each", len(slides), duration)
    run_command(slideshow_command(slides, duration))
