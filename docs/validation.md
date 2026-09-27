# Release validation

Local verification on 2026-09-27, macOS arm64, Python 3.14.0:

| Check | Result |
| --- | --- |
| `ruff check .` | PASS |
| `ruff format --check .` | PASS |
| `mypy src` (strict) | PASS, 14 application source files |
| `pytest -q` | PASS, 69 tests |
| Regular package build/install in an isolated venv | PASS |
| Installed `pipresent --help` | PASS |
| Installed `pipresent doctor` | Correctly exits 1: mpv, LibreOffice and pdftoppm absent |
| Doctor with writable workspace XDG paths | Directory checks PASS; no display/cache warnings expected |
| `sh -n` for installer, uninstaller and start launcher | PASS |
| Installer config lifecycle with mocked package installation | PASS; preserves unrelated autostart and cached data |
| GitHub Actions | PASS: all six jobs in release-polish run [36352949119](https://github.com/pierrickvhk/pipresent/actions/runs/36352949119) |
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

## Release-polish verification

The previously published run [36352217400](https://github.com/pierrickvhk/pipresent/actions/runs/36352217400)
passed Linux/macOS and failed both Windows jobs. The fixes retain fsync and atomic replacement:
imports use writable descriptors, and installer temporary files close before replacement.
Regression tests enforce writable descriptors, closed handles, unchanged file contents and
preservation of previous data on sync/replacement failures. No Windows jobs were removed or skipped.

The public README was redesigned; the technical and Dutch guides retain operational detail.
The CI badge points at the actual `main` workflow. Raspberry Pi acceptance remains outstanding.

Release-polish commit `c11bf1cd814896fe7ce1a54b38992598544a07a5` passed all six jobs in
[run 36352949119](https://github.com/pierrickvhk/pipresent/actions/runs/36352949119):
Linux, macOS and Windows × Python 3.11 and 3.13. Each job ran Ruff lint/format, mypy,
all 69 tests and CLI help. This verifies the Windows fixes on actual Windows runners.

The GitHub-rendered README was inspected for headings, badges, links, callouts and Mermaid
rendering. The diagram was changed to a vertical layout for narrow-screen readability.
Repository description and all eight requested topics were applied through GitHub's API.
The [live workflow](https://github.com/pierrickvhk/pipresent/actions/workflows/ci.yml) reports
checks for subsequent documentation-only commits; hardware status remains unchanged.
