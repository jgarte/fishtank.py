"""
fishtank
--------
author: bczsalba


An interactive fishtank for your terminal.
"""

import os
import json


def to_local(subpath):
    """ Return joined path of dirname(__file__) and subpath """

    return os.path.join(os.path.dirname(__file__), subpath)


with open(to_local("data/species.json"), "r") as f:
    SPECIES_DATA = json.load(f)
