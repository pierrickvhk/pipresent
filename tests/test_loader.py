from pathlib import Path
from unittest.mock import patch

import pytest

from pipresent.config import PiPresentError
from pipresent.loader import acquire, discover_usb, import_content, load_cached, usb_candidates
from pipresent.paths import AppPaths


def source(root: Path, name: str = "usb") -> Path:
    drive = root / name
    drive.mkdir(parents=True)
    (drive / "talk.mp4").write_bytes(b"video")
    return drive


def test_candidates(tmp_path: Path) -> None:
    root = tmp_path / "mounts"
    assert usb_candidates(root) == []
    (root / "empty").mkdir(parents=True)
    assert discover_usb(root, 0) is None
    drive = source(root)
    assert discover_usb(root, 0) == drive
    source(root, "other")
    with pytest.raises(PiPresentError, match="Multiple potential"):
        discover_usb(root, 0)


def test_config_only_is_not_ignored(tmp_path: Path) -> None:
    drive = tmp_path / "usb"
    drive.mkdir()
    (drive / "presentation.json").write_text("{}")
    assert usb_candidates(tmp_path) == [drive]


def test_import_survives_usb_removal(tmp_path: Path, paths: AppPaths) -> None:
    drive = source(tmp_path)
    media, config = import_content(drive, paths)
    (drive / "talk.mp4").unlink()
    assert media.read_bytes() == b"video"
    assert load_cached(paths) == (media, config)
    assert acquire(paths, tmp_path / "absent", 0) == (media, config)


def test_failed_copy_preserves_cache(tmp_path: Path, paths: AppPaths) -> None:
    drive = source(tmp_path)
    previous = import_content(drive, paths)
    with patch("pipresent.loader.shutil.copyfile", side_effect=OSError("disk full")):
        with pytest.raises(OSError, match="disk full"):
            import_content(drive, paths)
    assert load_cached(paths) == previous
    assert not list((paths.data / "imports").glob(".staging-*"))


def test_invalid_usb_fails_even_with_cache(tmp_path: Path, paths: AppPaths) -> None:
    root = tmp_path / "mounts"
    drive = source(root)
    import_content(drive, paths)
    (drive / "presentation.json").write_text('{"content":"absent.pdf"}')
    with pytest.raises(PiPresentError, match="missing"):
        acquire(paths, root, 0)


def test_no_cache(paths: AppPaths) -> None:
    with pytest.raises(PiPresentError, match="No usable cached"):
        load_cached(paths)


def test_corrupt_pointer(paths: AppPaths) -> None:
    paths.ensure()
    (paths.data / "current").write_text("../../outside")
    with pytest.raises(PiPresentError, match="Invalid cache pointer"):
        load_cached(paths)


def test_wait_for_late_mount(tmp_path: Path) -> None:
    drive = tmp_path / "usb"
    with (
        patch("pipresent.loader.usb_candidates", side_effect=[[], [drive]]),
        patch("pipresent.loader.time.sleep") as sleep,
    ):
        assert discover_usb(tmp_path, 1) == drive
        sleep.assert_called_once()
