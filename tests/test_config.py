import json
from pathlib import Path

import pytest

from pipresent.config import Config, PiPresentError, load_config, select_content, validate_media


def test_missing_configuration(tmp_path: Path) -> None:
    assert load_config(tmp_path) == Config()


def test_valid_configuration(tmp_path: Path) -> None:
    (tmp_path / "talk.pptx").write_bytes(b"content")
    (tmp_path / "presentation.json").write_text('{"content":"talk.pptx","slide_duration":2.5}')
    media, config = select_content(tmp_path)
    assert media.name == "talk.pptx"
    assert config.slide_duration == 2.5


@pytest.mark.parametrize("value", [0, -1, True, "8", None, float("nan"), float("inf")])
def test_invalid_duration(tmp_path: Path, value: object) -> None:
    (tmp_path / "presentation.json").write_text(json.dumps({"slide_duration": value}))
    with pytest.raises(PiPresentError, match="positive"):
        load_config(tmp_path)


@pytest.mark.parametrize("value", ["{", "[]", "null"])
def test_invalid_json(tmp_path: Path, value: str) -> None:
    (tmp_path / "presentation.json").write_text(value)
    with pytest.raises(PiPresentError):
        load_config(tmp_path)


@pytest.mark.parametrize("name", ["../x.pdf", "/x.pdf", "a\\b.pdf", "", None])
def test_invalid_content_name(tmp_path: Path, name: object) -> None:
    (tmp_path / "presentation.json").write_text(json.dumps({"content": name}))
    with pytest.raises(PiPresentError):
        load_config(tmp_path)


def test_configured_missing_never_selects_other(tmp_path: Path) -> None:
    (tmp_path / "other.mp4").write_bytes(b"video")
    (tmp_path / "presentation.json").write_text('{"content":"missing.pdf"}')
    with pytest.raises(PiPresentError, match="missing"):
        select_content(tmp_path)


def test_zero_one_many(tmp_path: Path) -> None:
    with pytest.raises(PiPresentError, match="No supported"):
        select_content(tmp_path)
    first = tmp_path / "a.pdf"
    first.write_bytes(b"pdf")
    assert select_content(tmp_path)[0] == first
    (tmp_path / "b.mp4").write_bytes(b"video")
    with pytest.raises(PiPresentError, match="presentation.json"):
        select_content(tmp_path)


@pytest.mark.parametrize("extension", [".pptx", ".pdf", ".mp4", ".mkv", ".mov", ".PDF"])
def test_extensions(tmp_path: Path, extension: str) -> None:
    path = tmp_path / ("media" + extension)
    path.write_bytes(b"media")
    assert validate_media(path) == path


def test_unsupported_and_empty(tmp_path: Path) -> None:
    with pytest.raises(PiPresentError, match="Unsupported"):
        validate_media(tmp_path / "a.txt")
    path = tmp_path / "a.pdf"
    path.touch()
    with pytest.raises(PiPresentError, match="empty"):
        validate_media(path)
