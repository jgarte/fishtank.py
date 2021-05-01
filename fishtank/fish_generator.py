"""
fishtank.generate_fish
----------------------
author: bczsalba


This module provieds a function to generate a file containing set of pre-defined FishProperties from
the data it was given. While this is accessible through the command line, it should be more
user-accessible.

example for output:

class Molly():
    \"\"\" Organizer class for variaties of Molly \"\"\"

    Golden_Panda: FishProperties = {
        "stages": [">->", "><'>", ">-<'>"],
        "type": FishType.MID_WATER,
        "speed": 3,
        "variant": "golden_panda",
        "species": "Molly",
        "pos": [0, 0],
        "age": 0,
        "chance": 15,
        "dominance": 30,
        "pigment": [214, 220, 221, 232, 234],
    }
    ...

These can then be used in interface.py as:

```py
from fish_types import Molly
aquarium = Aquarium()
aquarium += Fish(aquarium, Molly.Golden_Panda)
```
"""

import os
import sys
import json
from typing import Any

from . import to_local

FILE_TEMPLATE = """\
\"\"\"
fishtank.fish_types
-------------------
author: fishtank.py :)


This is a file generated by fish tank for easy access to fish types.
For more information, check out fishtank.fish_generator!
\"\"\"

# these classes are only used for organization purposes, and as such
# provide no class methods.
#
# pylint: disable=too-few-public-methods

from random import randint
from .enums import FishProperties, FishType

def random(cls: object) -> FishProperties:
    \"\"\" Return a random element from class \"\"\"

    options = [attr for attr in dir(cls) if not attr.startswith('_') and not attr == "random"]
    output = getattr(cls, options[randint(0, len(options) - 1)])
 
    # mypy complains that output is of type Any, but we know it cannot be.
    return output  # type: ignore

"""


def generate_inner_dict(
    data: dict[str, Any], attributes: list[str], parent_data: dict[str, Any]
) -> dict[str, Any]:
    """Generate inner (variants, specials) dict"""

    out_data = {key: parent_data.get(key) for key in attributes}

    for key, value in data.items():
        out_data[key] = value

    return out_data


def generate_lines(values: dict[str, Any], title: str) -> tuple[list[str], list[str]]:
    """Generate lines from values and title"""

    lines = []
    lines.append(4 * " " + f"{title}: FishProperties = " + "{")
    attributes = []

    for key, value in values.items():
        if key in ["variants", "specials"]:
            continue

        if key == "type":
            value = f"FishType.{value.upper()}"

        elif isinstance(value, str):
            value = f'"{value}"'

        attributes.append(key)
        lines.append(8 * " " + f'"{key}": {value},')

    lines.append(4 * " " + "}\n")

    return lines, attributes


# pylint: disable=too-many-locals
def generate_fish(path: str) -> None:
    """Generate fish_types.py file from json"""

    if not os.path.isfile(path):
        print(f'"{path}" is not a file!')
        sys.exit(1)

    with open(path, "r") as datafile:
        data = json.load(datafile)

    lines = []
    for species, values in data.items():
        values["species"] = species
        values["pos"] = [0, 0]
        values["age"] = 0
        title = species.title()

        lines.append(f"class {title}:")
        lines.append(" " * 4 + f'""" Organizer class for variaties of {title} """\n')
        newlines, attributes = generate_lines(values, title)
        lines += newlines

        if (variants := values.get("variants")) is not None:
            for variant, variant_data in variants.items():
                inner_data = generate_inner_dict(variant_data, attributes, values)
                inner_data["variant"] = variant

                inner_lines, _ = generate_lines(inner_data, variant.title())
                lines += inner_lines

        if (specials := values.get("specials")) is not None:
            for special, special_data in specials.items():
                inner_data = generate_inner_dict(special_data, attributes, values)

                inner_lines, _ = generate_lines(inner_data, special.title())
                lines += inner_lines

    # print(lines)
    with open(to_local("fish_types.py"), "w") as outfile:
        outfile.write(FILE_TEMPLATE + "\n".join(lines))
