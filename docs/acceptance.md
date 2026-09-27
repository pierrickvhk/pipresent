# Raspberry Pi acceptance checklist

**MANUAL RASPBERRY PI TEST REQUIRED** for every item below. None has been claimed as passed.
Use a Pi 4 or newer with current 64-bit Raspberry Pi OS Desktop, an HDMI display and a USB drive.
Record OS image, Pi model, mpv/LibreOffice versions, filenames and observations when testing.

- [ ] Install succeeds on Raspberry Pi OS as the desktop user.
- [ ] `pipresent doctor` passes; investigate warnings.
- [ ] MP4 opens fullscreen.
- [ ] MP4 loops repeatedly without restarting mpv (observe PID with `pgrep -a mpv`).
- [ ] PPTX converts successfully, including a deck using installed presentation fonts.
- [ ] PDF converts successfully.
- [ ] Slides are in correct order (use at least 12 numbered slides).
- [ ] Slideshow loops back to slide 1 at the configured duration.
- [ ] USB presentation imports locally.
- [ ] USB can be safely ejected and removed during playback.
- [ ] Cached content survives reboot without USB.
- [ ] Autostart launches after the desktop session, with desktop auto-login enabled.
- [ ] Screen remains fullscreen across many loops, with screen blanking disabled.
- [ ] Logs can be inspected and show import/conversion/playback events.
- [ ] Invalid JSON, a missing configured file and two candidate drives fail clearly.
- [ ] Removing an invalid USB allows the previous cache to play.
- [ ] Reinstall does not duplicate autostart or alter other desktop entries.
- [ ] Uninstall preserves data and unrelated autostart entries.

Use a video without encoded black frames when assessing loop behaviour. Report any decoder
or display gaps separately from player-process restarts. Run at least a 30-minute soak test
before relying on a behind-the-TV deployment.
