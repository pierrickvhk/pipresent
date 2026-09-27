from pathlib import Path
from unittest.mock import patch

import pytest

from pipresent.config import Config, PiPresentError
from pipresent.paths import AppPaths
from pipresent.router import play


@pytest.mark.parametrize("extension", ["mp4", "mkv", "mov"])
def test_video(tmp_path: Path, paths: AppPaths, extension: str) -> None:
    media = tmp_path / f"x.{extension}"
    media.write_bytes(b"video")
    with patch("pipresent.router.play_video") as player:
        play(media, Config(), paths)
        player.assert_called_once_with(media)


@pytest.mark.parametrize("extension", ["pptx", "pdf"])
def test_document(tmp_path: Path, paths: AppPaths, extension: str) -> None:
    media = tmp_path / f"x.{extension}"
    media.write_bytes(b"document")
    with (
        patch("pipresent.router.render_powerpoint", return_value=tmp_path / "x.pdf") as ppt,
        patch("pipresent.router.render_pdf", return_value=[tmp_path / "slide-1.png"]) as pdf,
        patch("pipresent.router.play_slideshow") as player,
    ):
        play(media, Config(slide_duration=3), paths)
        assert ppt.call_count == (1 if extension == "pptx" else 0)
        pdf.assert_called_once()
        player.assert_called_once_with([tmp_path / "slide-1.png"], 3)
    assert list(paths.cache.iterdir()) == []


def test_unsupported(tmp_path: Path, paths: AppPaths) -> None:
    with pytest.raises(PiPresentError, match="Unsupported"):
        play(tmp_path / "x.doc", Config(), paths)
