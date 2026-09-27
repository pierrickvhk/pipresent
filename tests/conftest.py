from pathlib import Path

import pytest

from pipresent.paths import AppPaths


@pytest.fixture
def paths(tmp_path: Path) -> AppPaths:
    return AppPaths(tmp_path / "data", tmp_path / "cache", tmp_path / "state")
