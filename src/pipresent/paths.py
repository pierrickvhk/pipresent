"""User-local XDG directories; no system writes."""

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    data: Path
    cache: Path
    state: Path

    @classmethod
    def discover(cls) -> "AppPaths":
        def xdg(name: str, default: str) -> Path:
            value = Path(os.environ.get(name, str(Path.home() / default)))
            return (value if value.is_absolute() else Path.home() / default) / "pipresent"

        return cls(
            xdg("XDG_DATA_HOME", ".local/share"),
            xdg("XDG_CACHE_HOME", ".cache"),
            xdg("XDG_STATE_HOME", ".local/state"),
        )

    def ensure(self) -> None:
        for path in (self.data, self.cache, self.state):
            path.mkdir(parents=True, exist_ok=True)
