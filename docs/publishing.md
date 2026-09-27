# Release maintenance

Public repository: [pierrickvhk/pipresent](https://github.com/pierrickvhk/pipresent).
The default branch is `main`. The source version is 0.1.0; a version badge alone does not
indicate a published GitHub release or completed hardware acceptance.

## Before a release

1. Run Ruff lint/format checks, strict mypy and pytest.
2. Push the reviewed commits and check all six jobs in the [CI matrix](https://github.com/pierrickvhk/pipresent/actions/workflows/ci.yml).
3. Complete [acceptance.md](acceptance.md) on a real Raspberry Pi and record the hardware,
   OS image, tool versions and observations in [validation.md](validation.md).
4. Update the changelog and hardware status only with results actually observed.
5. Commit and push those records before tagging a release.

With [GitHub CLI](https://cli.github.com/) installed and authenticated:

```bash
git tag -a v0.1.0 -m "PiPresent v0.1.0"
git push origin main --follow-tags
gh release create v0.1.0 --repo pierrickvhk/pipresent \
  --title "PiPresent v0.1.0" --generate-notes
```

## Repository metadata

Description:

> Plug-and-play PowerPoint, PDF and video presentation player for Raspberry Pi displays.

Topics: `raspberry-pi`, `python`, `automation`, `digital-signage`, `powerpoint`, `mpv`, `kiosk`, `linux`.

To apply these values manually, use the repository's About settings, or:

```bash
gh repo edit pierrickvhk/pipresent \
  --description "Plug-and-play PowerPoint, PDF and video presentation player for Raspberry Pi displays." \
  --add-topic raspberry-pi,python,automation,digital-signage,powerpoint,mpv,kiosk,linux
```
