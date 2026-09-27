import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from pipresent.commands import run_command
from pipresent.config import PiPresentError
from pipresent.players.slideshow import slideshow_command
from pipresent.players.video import play_video, video_command
from pipresent.renderers.pdf import pdf_command, render_pdf
from pipresent.renderers.powerpoint import powerpoint_command, render_powerpoint


def test_video_one_process(tmp_path: Path) -> None:
    path = tmp_path / "a video.mp4"
    args = video_command(path)
    assert "--loop-file=inf" in args
    assert "--loop-playlist=inf" not in args
    assert args[-2:] == ["--", str(path)]
    with patch("pipresent.commands.subprocess.run") as run:
        play_video(path)
        run.assert_called_once_with(args, check=True, timeout=None)


def test_slideshow_command(tmp_path: Path) -> None:
    args = slideshow_command([tmp_path / "slide-10.png", tmp_path / "slide-2.png"], 8)
    assert "--image-display-duration=8" in args
    assert "--loop-playlist=inf" in args
    assert args[-1].endswith("slide-10.png")
    with pytest.raises(PiPresentError, match="No slides"):
        slideshow_command([], 8)


def test_conversion_commands(tmp_path: Path) -> None:
    pdf = pdf_command(tmp_path / "x.pdf", tmp_path)
    assert pdf == [
        "pdftoppm",
        "-png",
        "-scale-to",
        "1920",
        str(tmp_path / "x.pdf"),
        str(tmp_path / "slide"),
    ]
    ppt = powerpoint_command(tmp_path / "x.pptx", tmp_path, tmp_path / "profile")
    assert ppt[0] == "libreoffice"
    assert ppt[1] == f"-env:UserInstallation={(tmp_path / 'profile').as_uri()}"
    assert ppt[2:5] == ["--headless", "--convert-to", "pdf"]


@pytest.mark.parametrize(
    "error",
    [
        FileNotFoundError(),
        subprocess.CalledProcessError(2, "mpv"),
        subprocess.TimeoutExpired("mpv", 1),
    ],
)
def test_command_errors(error: Exception) -> None:
    with patch("pipresent.commands.subprocess.run", side_effect=error):
        with pytest.raises(PiPresentError) as caught:
            run_command(["mpv", "x"])
        assert caught.value.__cause__ is error


def test_conversion_missing_output(tmp_path: Path) -> None:
    with patch("pipresent.renderers.powerpoint.run_command"):
        with pytest.raises(PiPresentError, match="did not produce"):
            render_powerpoint(tmp_path / "x.pptx", tmp_path)
    with patch("pipresent.renderers.pdf.run_command"):
        with pytest.raises(PiPresentError, match="no usable slides"):
            render_pdf(tmp_path / "x.pdf", tmp_path)
