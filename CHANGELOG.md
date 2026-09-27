# Changelog

## v0.1.0

- Cross-platform durability fix: sync writable import descriptors and close installer temporary
  files before atomic replacement, including Windows regression coverage.
- Redesigned public README with separate Dutch and technical guides.

- Deterministic mounted-USB ingestion with strict JSON configuration validation.
- Staged local caching, unchanged-content reuse and previous-import retention.
- PPTX support through headless LibreOffice and PDF support through Poppler.
- MP4, MKV and MOV video support with persistent fullscreen mpv file looping.
- Numerically ordered fullscreen slideshow playlists with configurable duration.
- `start`, `play`, `doctor` and help/version CLI commands.
- Diagnostics, external-command errors and rotating application logs.
- User-local venv installer, safe optional Raspberry Pi labwc autostart and uninstaller.
- Unit tests, Ruff, strict mypy and cross-platform GitHub Actions configuration.
- Installation, architecture, troubleshooting and manual hardware acceptance documentation.

Source published at https://github.com/pierrickvhk/pipresent. Raspberry Pi hardware acceptance remains pending.
