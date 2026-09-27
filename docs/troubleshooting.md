# Troubleshooting

Start in a terminal inside the Pi's desktop:

```bash
~/.local/bin/pipresent doctor
~/.local/bin/pipresent start --wait 7
tail -n 100 ~/.local/state/pipresent/pipresent.log
tail -n 100 ~/.local/state/pipresent/autostart.log
```

Adjust paths if you configured XDG overrides. Application events go to the rotating log;
LibreOffice, Poppler and mpv output appears in the terminal or autostart log.

| Symptom | Check and action |
| --- | --- |
| USB not detected | Open the drive in the desktop file manager. Confirm it is mounted under `/media/$(whoami)/DRIVE`; files must be at the drive root. Try `start --usb-root /actual/mount/parent --wait 10`. PiPresent does not mount disks. |
| Multiple USB sources | Leave only one drive containing supported media or `presentation.json`. Unrelated drives can remain. |
| Missing configured content | Check exact spelling/case of `content` and filename. A configured missing file intentionally fails; it does not select another file. |
| No supported files | Use `.pptx`, `.pdf`, `.mp4`, `.mkv` or `.mov`. A USB with unrelated files is ignored; without a cache startup fails. |
| mpv unavailable | Run `sudo apt install mpv`, then `pipresent doctor`. |
| LibreOffice unavailable | Run `sudo apt install libreoffice-impress`; executable name is `libreoffice`. |
| pdftoppm unavailable | Run `sudo apt install poppler-utils`. |
| PowerPoint formatting differs | Install the presentation's fonts; inspect LibreOffice export. Export PDF from PowerPoint for more predictable layout. |
| Animations or embedded video missing | Expected in v0.1: PowerPoint is converted to static slides. Export an MP4 if motion is essential. |
| Screen goes blank | Disable Screen Blanking in Control Centre → Display, or Raspberry Pi Configuration on older images. Check TV sleep/eco settings too. See the [official instructions](https://www.raspberrypi.com/documentation/computers/configuration.html#screen-blanking). |
| Does not start at boot | Enable desktop auto-login, run installer with `--autostart`, inspect the marked block in `~/.config/labwc/autostart`, and check logs. A console-only boot cannot start a Wayland GUI. Other desktops need their own autostart configuration. |
| Wayland/display errors | Run from the logged-in desktop, not root or a plain SSH session. Check `WAYLAND_DISPLAY`, `DISPLAY` and `XDG_RUNTIME_DIR`; do not hardcode someone else's display credentials. |
| Brief black video interval | PiPresent keeps the same mpv process alive, but encoded black frames and decoder/display behaviour remain. Inspect source media and test a different codec on the Pi. |
| Conversion failed or timed out | Test an unencrypted, small PDF/deck; inspect external-tool output. Conversions have a five-minute limit. Check available disk space and memory. |
| Command not found | Use `~/.local/bin/pipresent`, or add `~/.local/bin` to PATH. |
| No audio | Video audio follows mpv/system output. Check HDMI audio settings, TV volume and source track. |

## Cache recovery

Stop PiPresent first (`q` in mpv or Ctrl+C in the launching terminal). Remove an invalid USB
source and restart to use the active cache. Failed copies do not replace that cache.

If the latest import copied successfully but cannot render, the previous import normally
remains under `~/.local/share/pipresent/imports/`. Inspect `current` and the other UUID
directory's `presentation.json`. Copy the desired previous media/configuration to a USB drive
and import it again. This is safer than hand-editing the active pointer. To test a file first:

```bash
pipresent play /path/to/replacement.pdf
```

While PiPresent is stopped, stale `render-*` directories in `~/.cache/pipresent/` and
`.staging-*` directories under its imports directory may be removed. Do not delete the active
or previous import. Ensure sufficient space for current, previous and staged content plus PNGs.
Autostart output is not rotated; truncate its log while stopped if it grows too large.

## Disable autostart or uninstall

Remove only the lines between `# PiPresent BEGIN` and `# PiPresent END`, including markers,
from `~/.config/labwc/autostart`. Keep other entries. The first original file is backed up
alongside it; do not restore that backup over unrelated changes made since installation.

`./scripts/uninstall.sh` removes the owned installation and block but keeps data.
`./scripts/uninstall.sh --purge` displays the application paths and asks you to type `PURGE`.
Use the same user and XDG environment as installation. Neither mode removes apt packages.
