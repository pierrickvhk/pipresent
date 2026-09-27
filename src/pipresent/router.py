"""Route local media; own temporary render lifetime through playback."""

import tempfile
from pathlib import Path

from pipresent.config import Config, validate_media
from pipresent.paths import AppPaths
from pipresent.players.slideshow import play_slideshow
from pipresent.players.video import play_video
from pipresent.renderers.pdf import render_pdf
from pipresent.renderers.powerpoint import render_powerpoint


def play(path: Path, config: Config, paths: AppPaths) -> None:
    validate_media(path)
    if path.suffix.lower() in {".mp4", ".mkv", ".mov"}:
        play_video(path)
        return
    paths.ensure()
    with tempfile.TemporaryDirectory(prefix="render-", dir=paths.cache) as temporary:
        directory = Path(temporary)
        pdf = render_powerpoint(path, directory) if path.suffix.lower() == ".pptx" else path
        slides = render_pdf(pdf, directory / "slides")
        play_slideshow(slides, config.slide_duration)
