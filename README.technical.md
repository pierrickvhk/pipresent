# PiPresent — technical guide

[Project overview](README.md) · [Dutch user guide](README.nl.md) · [Architecture](docs/architecture.md)

Operational details and developer reference for Raspberry Pi OS Desktop. For the design
rationale and conversion pipeline, see the architecture guide.

**MANUAL RASPBERRY PI TEST REQUIRED.** See the [acceptance checklist](docs/acceptance.md).

## Quick start

Clone the public repository on your Raspberry Pi desktop:

```bash
git clone https://github.com/pierrickvhk/pipresent.git
cd pipresent
./scripts/install.sh --autostart
```

Run the installer **as the desktop user, without sudo**. It requests sudo only for apt.
An internet connection is required to install packages. It creates an isolated virtual
environment and a launcher at `~/.local/bin/pipresent`.

Prepare a USB drive, insert it, then launch from the Pi desktop:

```bash
~/.local/bin/pipresent start
```

For unattended boot, enable **desktop auto-login** using Raspberry Pi configuration tools,
and disable screen blanking. Reboot with the drive inserted. Once fullscreen playback
begins, use the desktop's safe-eject action before removing the USB drive.

## Preparing a USB drive

Put files in the drive's root, not inside a subfolder:

```text
USB/
├── presentation.pptx
└── presentation.json
```

```json
{
  "content": "presentation.pptx",
  "slide_duration": 8
}
```

`presentation.json` is optional when exactly one supported file exists. Without it:

| Supported files | Result |
| --- | --- |
| Zero | Drive is ignored during discovery; cache is used if no source appears |
| One | That file is selected |
| Multiple | Error; specify `content` in `presentation.json` |

`content` must be a filename in the USB root, without path separators. Matching is exact;
extensions are case-insensitive. Symlinked media and empty files are rejected. If a configured
file is missing or unsupported, PiPresent stops with a clear error. It never silently chooses
another file. `slide_duration` must be a positive finite JSON number; the default is 8 seconds.
Unknown JSON keys are ignored. Duration is ignored for video.

Mounted drives are discovered under `/media/<current-user>/`. A directory is a potential
source if it contains `presentation.json` or a supported filename. Unrelated drives are
ignored; multiple potential sources cause an error. PiPresent waits up to seven seconds for
a source, then uses the cache. It does not mount drives itself or watch for later insertions.
Discovery stops when a source is found; attach all drives before launching.

## Supported formats and PowerPoint behaviour

| Format | Playback |
| --- | --- |
| `.pptx` | LibreOffice → PDF → PNG → static slideshow |
| `.pdf` | pdftoppm → PNG → static slideshow |
| `.mp4`, `.mkv`, `.mov` | mpv video loop, with source audio |

**PowerPoint animations, Morph transitions, embedded video playback, interactive content
and PowerPoint-specific effects are not supported in v0.1.** Every slide uses the same duration.
Install the fonts used by your presentation on the Pi; LibreOffice can lay out slides differently
from Microsoft PowerPoint. Exporting to PDF beforehand provides more predictable layout.
File extensions identify the route; successful decoding still depends on valid media and codecs.

## Installation and autostart

```bash
./scripts/install.sh             # manual launch only
./scripts/install.sh --autostart # also launch after labwc starts
```

The installer installs `python3`, `python3-venv`, `python3-pip`, `mpv`,
`libreoffice-impress` and `poppler-utils`, installs this checkout as a regular package in
`~/.local/share/pipresent-app/venv`, creates runtime directories, and runs `doctor`.
Add `~/.local/bin` to your shell PATH if you want the short `pipresent` command.
Run the installer again after updating the checkout. It refuses unrelated installation paths
or launchers. Changing XDG settings between installation and uninstallation is unsupported.

Autostart appends a `# PiPresent BEGIN` / `# PiPresent END` block to
`~/.config/labwc/autostart`, preserving other entries. The original file is backed up as
`autostart.pipresent.bak` on the first edit. Reinstalling does not duplicate the block.
The launcher runs in the background after the desktop session starts; no system service is used.
On older Bookworm desktops using Wayfire/X11, use that desktop's own session autostart mechanism.

To disable automatic startup, remove only the marked block. To uninstall:

```bash
./scripts/uninstall.sh         # keeps presentations, cache and logs
./scripts/uninstall.sh --purge # shows paths and requires typing PURGE
```

Quit playback with `q` (or Ctrl+C in its terminal) before updating/uninstalling. Uninstall
removes the owned application, launcher and autostart block. It leaves apt packages and the
original autostart backup in place. Purge permanently deletes PiPresent application data only.

## CLI

```bash
pipresent --help
pipresent --version
pipresent doctor
pipresent start
pipresent start --wait 3 --usb-root /media/myuser
pipresent play /path/to/video.mp4
pipresent play /path/to/slides.pdf --slide-duration 5
```

`start` imports USB media before playback; `play` directly uses the supplied path and does
not import it. Do not remove a drive used by `play`. Run one PiPresent instance per desktop.
Playback ends when you press `q` in mpv; an unexpected player exit is logged, not restarted.
Errors return exit code 1, invalid CLI arguments 2, and Ctrl+C 130.

`doctor` reports PASS/WARN/FAIL, exits 1 for missing tools or unwritable directories, and
warns about an absent display environment or cache. Display variables do not prove that a
Wayland connection or HDMI output works; test playback on the actual Pi.

## Storage and logs

| Default directory | Purpose |
| --- | --- |
| `~/.local/share/pipresent/` | Imported media, config and active `current` pointer |
| `~/.cache/pipresent/` | Temporary PDF, LibreOffice profile and PNG slides |
| `~/.local/state/pipresent/pipresent.log` | Rotating application log (2 MB × four files) |
| `~/.local/state/pipresent/autostart.log` | Session launcher and external-tool output |

Absolute `XDG_DATA_HOME`, `XDG_CACHE_HOME`, `XDG_STATE_HOME`, and installer
`XDG_CONFIG_HOME` overrides are honored; relative overrides fall back to defaults.
The installed launcher remembers the data/cache/state locations selected at installation.
Autostart output is appended and is not rotated; inspect and truncate it occasionally while
playback is stopped. Interrupted renders may leave cache directories; these can be removed
while PiPresent is stopped. Never place unrelated files in PiPresent's dedicated directories.

## Screen blanking and troubleshooting

Disable screen blanking using Raspberry Pi OS **Control Centre → Display → Screen Blanking**
(on older releases, Raspberry Pi Configuration → Display). You can also use
`sudo raspi-config` and its Display Options → Screen Blanking setting. Menu names can differ
between images; see the [official Raspberry Pi documentation](https://www.raspberrypi.com/documentation/computers/configuration.html#screen-blanking).
PiPresent deliberately does not alter display power settings or desktop auto-login.

Start with `pipresent doctor` and the application log. See the
[troubleshooting guide](docs/troubleshooting.md) for USB, fonts, conversion, display and boot issues.

## Development and testing

Python 3.11+ on Linux, macOS or Windows is sufficient for unit tests:

```bash
python -m venv .venv
# Linux/macOS:
. .venv/bin/activate
# Windows PowerShell instead: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
ruff check .
ruff format --check .
mypy src
pytest -q
pipresent --help
```

Tests use temporary directories and mock subprocesses; no Pi, USB, LibreOffice or GUI is
required. GitHub Actions defines Linux/macOS/Windows jobs on Python 3.11 and 3.13.
Check the [live CI workflow](https://github.com/pierrickvhk/pipresent/actions/workflows/ci.yml) for the current result. See [release validation](docs/validation.md) and the
[manual Pi acceptance checklist](docs/acceptance.md).

## Current limitations

- Startup-only import; no hot replacement, scheduling or mixed-media playlists.
- Requires an already mounted drive and an active graphical desktop session.
- Static slides, uniform timing, 1920-pixel longest edge; conversion can take time on large decks.
- Conversion times out after five minutes per tool. No progress screen during conversion.
- Invalid/ambiguous USB sources fail visibly in logs, even if a cache exists; remove the bad
  source to use the previous cache. No on-screen error UI yet.
- Import validation checks selection, extension, nonempty file and copy integrity, not renderability.
  A validly copied but corrupt document becomes current; the previous import is retained for recovery.
- Staging needs disk space for an additional import and generated slides. Sudden power loss,
  SD-card damage and concurrent starts are outside the atomic-copy guarantee.
- Content is processed by local desktop tools; use trusted presentations and keep the Pi updated.
