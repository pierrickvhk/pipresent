from pathlib import Path
from unittest.mock import patch

import pytest

from pipresent.cli import doctor, main
from pipresent.paths import AppPaths


def test_doctor_missing_tools(paths: AppPaths, capsys: pytest.CaptureFixture[str]) -> None:
    with patch("pipresent.cli.shutil.which", return_value=None):
        assert doctor(paths) == 1
    output = capsys.readouterr().out
    assert "FAIL mpv" in output
    assert "libreoffice-impress" in output
    assert "poppler-utils" in output
    assert "WARN Cached content" in output


def test_doctor_available_tools(paths: AppPaths) -> None:
    with patch("pipresent.cli.shutil.which", return_value="/usr/bin/tool"):
        assert doctor(paths) == 0


@pytest.mark.parametrize(
    "args",
    [
        ["start", "--wait", "nan"],
        ["start", "--wait", "-1"],
        ["play", "x.pdf", "--slide-duration", "0"],
    ],
)
def test_cli_rejects_bad_numbers(args: list[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(args)
    assert exc.value.code == 2


def test_manual_play(tmp_path: Path, paths: AppPaths) -> None:
    with (
        patch("pipresent.cli.AppPaths.discover", return_value=paths),
        patch("pipresent.cli.setup_logging"),
        patch("pipresent.cli.play") as play,
    ):
        assert main(["play", str(tmp_path / "x.mp4")]) == 0
        assert play.call_args.args[0] == tmp_path / "x.mp4"
