"""
fishtank
--------
author: bczsalba


An interactive fishtank for your terminal.
"""

import os
import sys
import json
from typing import Any, Tuple

__version__ = "0.0.0"
usage_data = f"""\
fishtank {__version__}:

- fishtank: run fishtank
- fishtank -h (--help): print this text
- fishtank -g (--generate-layouts): force-generate fishtank/layouts files
"""


def to_local(subpath: str) -> str:
    """Return joined path of dirname(__file__) and subpath"""

    return os.path.join(os.path.dirname(__file__), subpath)


with open(to_local("data/species.json"), "r") as species_file:
    SPECIES_DATA = json.load(species_file)
del species_file


# pylint: disable=protected-access
def get_caller(depth: int = 1) -> str:
    """
    Return caller of function with protected methods

    This is needed, because inspect tends to be slower,
    and less reliable for the same purpose.
    """

    frame = sys._getframe()
    for _ in range(depth + 1):
        frame = getattr(frame, "f_back")

    method = frame.f_code.co_name
    obj = frame.f_locals.get("self")

    return type(obj).__name__ + "." + method if obj else method


def dbg(*args: Any, end: str = "\n") -> None:
    """Write information to log file"""

    if args == tuple():
        args = (get_caller(2),)

    string = " ".join([str(a) for a in args])

    frame = sys._getframe()
    if frame is None:
        return

    frame_back = frame.f_back
    if frame_back is None:
        return

    filename = frame_back.f_code.co_filename.split("/")[-1]
    lineno = frame_back.f_lineno

    with open(to_local("log"), "a") as logfile:
        logfile.write(f"{filename}/{get_caller(0)}:{lineno} : " + string + end)
