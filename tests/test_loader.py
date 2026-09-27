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
    (drive / "talk.mp4").write_bytes(b"replacement video")
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


def test_unchanged_usb_reuses_import(tmp_path: Path, paths: AppPaths) -> None:
    drive = source(tmp_path)
    first = import_content(drive, paths)
    assert import_content(drive, paths) == first
    assert len(list((paths.data / "imports").iterdir())) == 1


def test_keep_current_and_previous(tmp_path: Path, paths: AppPaths) -> None:
    drive = source(tmp_path)
    for i in range(4):
        (drive / "talk.mp4").write_bytes(f"video {i}".encode())
        import_content(drive, paths)
    assert len(list((paths.data / "imports").iterdir())) == 2
    assert load_cached(paths)[0].read_bytes() == b"video 3"


def test_pointer_failure_preserves_cache(tmp_path: Path, paths: AppPaths) -> None:
    drive = source(tmp_path)
    first = import_content(drive, paths)
    (drive / "talk.mp4").write_bytes(b"changed")
    with patch("pipresent.loader.Path.replace", side_effect=OSError("replace failed")):
        with pytest.raises(OSError, match="replace failed"):
            import_content(drive, paths)
    assert load_cached(paths) == first


def test_source_changes_during_copy(tmp_path: Path, paths: AppPaths) -> None:
    import shutil

    drive = source(tmp_path)
    original_copy = shutil.copyfile

    def changing_copy(source: Path, destination: Path) -> Path:
        result = original_copy(source, destination)
        source.write_bytes(b"modified during copy")
        return result

    with patch("pipresent.loader.shutil.copyfile", side_effect=changing_copy):
        with pytest.raises(PiPresentError, match="changed during import"):
            import_content(drive, paths)
    assert not (paths.data / "current").exists()
