import runpy
from pathlib import Path

import pytest

helpers = runpy.run_path(str(Path(__file__).parents[1] / "scripts/manage_install.py"))
update = helpers["update_autostart"]
strip = helpers["without_block"]


def test_autostart_idempotence_and_removal(tmp_path: Path) -> None:
    path = tmp_path / "autostart"
    original = "# user's desktop\nother-app &\n"
    path.write_text(original)
    launcher = tmp_path / "space and 'quote" / "pipresent"
    log = tmp_path / "logs/output.log"
    update(path, launcher, log, True)
    first = path.read_text()
    update(path, launcher, log, True)
    assert path.read_text() == first
    assert first.count("# PiPresent BEGIN") == 1
    assert "2>&1 &" in first
    assert path.with_name("autostart.pipresent.bak").read_text() == original
    update(path, launcher, log, False)
    assert path.read_text() == original


@pytest.mark.parametrize(
    "text", ["# PiPresent BEGIN\n", "# PiPresent END\n", "# PiPresent END\n# PiPresent BEGIN\n"]
)
def test_malformed_markers(text: str) -> None:
    with pytest.raises(RuntimeError, match="Malformed"):
        strip(text)


def test_symlink_autostart_refused(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.write_text("untouched")
    link = tmp_path / "link"
    try:
        link.symlink_to(real)
    except OSError:
        pytest.skip("Symlinks unavailable on this platform")
    with pytest.raises(RuntimeError, match="symlink"):
        update(link, tmp_path / "launcher", tmp_path / "log", True)
    assert real.read_text() == "untouched"


def test_install_uninstall_lifecycle(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from unittest.mock import patch

    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    for name, value in (
        ("XDG_DATA_HOME", "data"),
        ("XDG_CACHE_HOME", "cache"),
        ("XDG_STATE_HOME", "state"),
        ("XDG_CONFIG_HOME", "config"),
    ):
        monkeypatch.setenv(name, str(tmp_path / value))
    autostart = tmp_path / "config/labwc/autostart"
    autostart.parent.mkdir(parents=True)
    autostart.write_text("unrelated-app &\n")
    main = helpers["main"]
    with (
        patch("sys.argv", ["manage_install.py", "install", "--autostart"]),
        patch("venv.EnvBuilder.create"),
        patch("subprocess.run") as run,
    ):
        assert main() == 0
        assert run.call_count == 2
        assert all(call.kwargs["check"] for call in run.call_args_list)
    launcher = tmp_path / ".local/bin/pipresent"
    assert launcher.exists()
    data = tmp_path / "data/pipresent/keep.pdf"
    data.write_bytes(b"user presentation")
    with patch("sys.argv", ["manage_install.py", "uninstall"]):
        assert main() == 0
    assert not launcher.exists()
    assert not (tmp_path / "data/pipresent-app").exists()
    assert data.read_bytes() == b"user presentation"
    assert autostart.read_text() == "unrelated-app &\n"


def test_unrelated_launcher_refused(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from unittest.mock import patch

    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    launcher = tmp_path / ".local/bin/pipresent"
    launcher.parent.mkdir(parents=True)
    launcher.write_text("user-owned script")
    with patch("sys.argv", ["manage_install.py", "uninstall"]):
        with pytest.raises(RuntimeError, match="unrelated launcher"):
            helpers["main"]()
    assert launcher.read_text() == "user-owned script"


def test_atomic_write_closes_before_replacement(tmp_path: Path) -> None:
    import tempfile
    from unittest.mock import patch

    handles = []
    real_temporary_file = tempfile.NamedTemporaryFile
    real_replace = Path.replace

    def temporary_file(*args: object, **kwargs: object) -> object:
        handle = real_temporary_file(*args, **kwargs)
        handles.append(handle)
        return handle

    def replace(source: Path, destination: Path) -> Path:
        assert handles and all(handle.closed for handle in handles)
        return real_replace(source, destination)

    path = tmp_path / "autostart"
    path.write_text("original")
    with (
        patch("tempfile.NamedTemporaryFile", side_effect=temporary_file),
        patch.object(Path, "replace", replace),
    ):
        helpers["atomic_write"](path, "replacement")
    assert path.read_text() == "replacement"
    assert list(tmp_path.iterdir()) == [path]


def test_atomic_write_failure_keeps_original(tmp_path: Path) -> None:
    from unittest.mock import patch

    path = tmp_path / "autostart"
    path.write_text("original")
    with patch.object(Path, "replace", side_effect=OSError("replace failed")):
        with pytest.raises(OSError, match="replace failed"):
            helpers["atomic_write"](path, "replacement")
    assert path.read_text() == "original"
    assert list(tmp_path.iterdir()) == [path]
