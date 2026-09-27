"""All external processes pass through one observable, testable boundary."""

import logging
import shlex
import subprocess
from collections.abc import Sequence

from pipresent.config import PiPresentError


def run_command(args: Sequence[str], *, timeout: float | None = None) -> None:
    logging.info("External command: %s", shlex.join(args))
    try:
        subprocess.run(list(args), check=True, timeout=timeout)
    except FileNotFoundError as exc:
        raise PiPresentError(f"Missing executable {args[0]}; run pipresent doctor") from exc
    except subprocess.CalledProcessError as exc:
        raise PiPresentError(f"{args[0]} failed with exit code {exc.returncode}") from exc
    except subprocess.TimeoutExpired as exc:
        raise PiPresentError(f"{args[0]} exceeded {timeout} seconds") from exc
