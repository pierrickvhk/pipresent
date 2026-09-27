from pathlib import Path

from pipresent.players.slideshow import slide_key


def test_natural_order() -> None:
    paths = [Path(f"slide-{n}.png") for n in (10, 2, 1, 100, 11)]
    assert [p.name for p in sorted(paths, key=slide_key)] == [
        "slide-1.png",
        "slide-2.png",
        "slide-10.png",
        "slide-11.png",
        "slide-100.png",
    ]
