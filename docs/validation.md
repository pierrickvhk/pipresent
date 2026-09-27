# Release validation

Local verification on 2026-09-27, macOS arm64, Python 3.14.0:

| Check | Result |
| --- | --- |
| `ruff check .` | PASS |
| `ruff format --check .` | PASS |
| `mypy src` (strict) | PASS, 14 application source files |
| `pytest -q` | PASS, 65 tests |
| Regular package build/install in an isolated venv | PASS |
| Installed `pipresent --help` | PASS |
| Installed `pipresent doctor` | Correctly exits 1: mpv, LibreOffice and pdftoppm absent |
| Doctor with writable workspace XDG paths | Directory checks PASS; no display/cache warnings expected |
| `sh -n` for installer, uninstaller and start launcher | PASS |
| Installer config lifecycle with mocked package installation | PASS; preserves unrelated autostart and cached data |
| GitHub Actions | PENDING publication; workflow configured, not executed remotely |
| Raspberry Pi/Linux installer and actual media playback | MANUAL RASPBERRY PI TEST REQUIRED |

The first doctor run also reported sandbox-denied home-directory writes; a second run used
workspace XDG paths and passed all directory checks. No graphical tools were installed on
this macOS machine. Missing target dependencies are not represented as successful Pi tests.

The macOS execution environment reapplied a hidden filesystem flag to an editable-install
`.pth` file, which Python 3.14 skips. Tests explicitly use the source tree via pytest's
`pythonpath` setting; installed CLI smoke checks use a normal, non-editable package install.
This does not change the Raspberry Pi installer, which already performs a regular install.

Tests cover strict config parsing, supported formats, deterministic discovery, cached fallback,
copy and pointer failure recovery, changed-during-copy detection, unchanged-content reuse,
retention, routing, conversion/player command construction, subprocess errors, natural slide
order, diagnostics, CLI validation, and installer/autostart preservation. External processes
are mocked; no rendered visual output or physical USB/HDMI behaviour was verified.

Complete [acceptance.md](acceptance.md) on a real Pi before deploying unattended or claiming
hardware readiness. Publish with [publishing.md](publishing.md), then inspect the actual CI run.
