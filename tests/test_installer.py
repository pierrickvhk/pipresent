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
