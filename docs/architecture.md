# Architecture

PiPresent keeps acquisition (`loader.py`), routing (`router.py`), rendering (`renderers/`)
and playback (`players/`) separate. The CLI supplies paths and configuration; runtime code
uses only Python's standard library.

## Ingestion and selection

`start` polls the current desktop user's `/media/<user>/` parent every 250 ms, for at most
seven seconds by default. It considers immediate mount directories containing a configuration
or a supported filename. It does not infer physical USB identity or call a mount tool: this
is a deliberately narrow Raspberry Pi Desktop convention. Non-USB mounts under that parent
can also qualify. Supply `--usb-root` for a different mount layout.

Multiple sources fail rather than choosing by arbitrary directory order. A present invalid
configuration is an error, not permission to use another file or silently fall back. No
qualifying source means use the last local import. Discovery exits on the first qualifying
scan, so a later-mounted second drive cannot be detected after playback starts.

## Local imports

Each import lives in `data/pipresent/imports/<UUID>/` with its own normalized configuration.
A plain `current` file holds only a validated UUID. A staged copy is checked for file size
and source changes during copying, its files are flushed with fsync, then the staging directory
is renamed and the active pointer is atomically replaced on the same filesystem. Staged files
are opened in non-truncating read/write mode for fsync compatibility on Windows. Installer
configuration writes likewise flush and close their temporary file before atomic replacement.

A failure before pointer replacement leaves the old pointer intact. Temporary files from
ordinary exceptions are cleaned up. Identical content/configuration reuses the existing
import. Successful replacement retains current and previous generations and removes older
UUID directories. Hard-killed staging directories may need manual cleanup. This is a
single-instance application; atomic replacement is not a multi-process lock or a guarantee
against filesystem/hardware failure during power loss.

Validation is structural, not full media decoding. Conversion occurs after import; if new
media cannot render, restore the previous generation as described in troubleshooting. Keeping
rendering outside ingestion makes video imports quick and avoids tying USB lifetime to GUI
playback. All `start` playback uses local files. Manual `play` intentionally bypasses import.

## Rendering

PPTX uses LibreOffice headless with a fresh file-URI user profile, avoiding connection to an
existing interactive instance. Conversion must return successfully and produce a nonempty PDF.
PDFs use `pdftoppm -png -scale-to 1920`; output must contain nonempty slide PNGs. Both tools
have a 300-second timeout. A per-run temporary cache directory owns intermediate files and
remains alive until mpv exits. Documents are re-rendered on each launch; rendered-slide reuse
is deferred to keep invalidation and font changes simple.

## Playback and process boundary

Every tool goes through `commands.run_command`: argument arrays, `subprocess.run`,
`check=True`, logging, and preserved underlying exceptions. Conversion has a timeout;
playback has none. External output inherits the terminal or autostart output log.

Video gets one mpv invocation with `--loop-file=inf`. There is no Python playback loop.
Slides use one invocation with natural numeric ordering, an image duration and
`--loop-playlist=inf`. `--no-config` avoids unexpected local mpv profiles changing appliance
behaviour. Absolute filenames and `--` protect mpv filenames from option interpretation.
The app does not synthesize transitions or repair black frames encoded in source media.

## Operations

A regular user-local venv avoids modifying Debian's externally managed system Python.
A marked labwc autostart block launches after login, inheriting Wayland session variables.
No root GUI process or pre-desktop system service is installed. Logs rotate at 2 MB with
three backups; external autostart output is a separate append-only log. `doctor` checks
executable availability, writable directories, display hints and the active import, without
launching graphics. It cannot certify actual display access or codec compatibility.
