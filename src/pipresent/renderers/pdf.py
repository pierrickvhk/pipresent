"""Rasterize PDFs at a bounded resolution suitable for HDMI displays."""

import logging
from pathlib import Path

from pipresent.commands import run_command
from pipresent.config import PiPresentError
from pipresent.players.slideshow import slide_key


def pdf_command(source: Path, output: Path) -> list[str]:
    return [
        "pdftoppm",
        "-png",
        "-scale-to",
        "1920",
        str(source.resolve()),
        str((output / "slide").resolve()),
    ]


def render_pdf(source: Path, output: Path) -> list[Path]:
    output.mkdir(parents=True, exist_ok=True)
    logging.info("PDF conversion: %s", source)
    run_command(pdf_command(source, output), timeout=300)
    slides = sorted(output.glob("slide-*.png"), key=slide_key)
    if not slides or any(path.stat().st_size == 0 for path in slides):
        raise PiPresentError("PDF conversion produced no usable slides")
    logging.info("Generated slide count: %d", len(slides))
    return slides
