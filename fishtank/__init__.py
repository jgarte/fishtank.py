"""
fishtank
--------
author: bczsalba


An interactive fishtank for your terminal.
"""

import os
import json

__version__ = "0.0.0"
usage_data = f"""\
fishtank {__version__}:

- fishtank: run fishtank
- fishtank -h (--help): print this text
- fishtank -g (--generate-layouts): force-generate fishtank/layouts files
"""


def to_local(subpath):
    """ Return joined path of dirname(__file__) and subpath """

    return os.path.join(os.path.dirname(__file__), subpath)


with open(to_local("data/species.json"), "r") as species_file:
    SPECIES_DATA = json.load(species_file)
del species_file


def dbg(string: str):
    """ Dump s to log file """

    with open(to_local("log"), "a") as logfile:
        logfile.write(string + "\n")
