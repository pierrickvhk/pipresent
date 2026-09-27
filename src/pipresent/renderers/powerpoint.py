"""Use an isolated LibreOffice profile to avoid desktop-instance conflicts."""

import logging
from pathlib import Path

from pipresent.commands import run_command
from pipresent.config import PiPresentError


def powerpoint_command(source: Path, output: Path, profile: Path) -> list[str]:
    return [
        "libreoffice",
        f"-env:UserInstallation={profile.resolve().as_uri()}",
        "--headless",
        "--convert-to",
        "pdf",
        "--outdir",
        str(output.resolve()),
        str(source.resolve()),
    ]


def render_powerpoint(source: Path, output: Path) -> Path:
    output.mkdir(parents=True, exist_ok=True)
    logging.info("PowerPoint conversion: %s", source)
    run_command(powerpoint_command(source, output, output / "lo-profile"), timeout=300)
    pdf = output / f"{source.stem}.pdf"
    if not pdf.is_file() or pdf.stat().st_size == 0:
        raise PiPresentError("LibreOffice did not produce a PDF; inspect presentation and fonts")
    return pdf
