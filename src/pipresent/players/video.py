"""Loop inside mpv, never by restarting its process."""

import logging
from pathlib import Path

from pipresent.commands import run_command
from pipresent.players import COMMON


def video_command(path: Path) -> list[str]:
    return [*COMMON, "--loop-file=inf", "--", str(path.resolve())]


def play_video(path: Path) -> None:
    logging.info("Video playback start: %s", path)
    run_command(video_command(path))
