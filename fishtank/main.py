"""
fishtank.main
-------------
author: bczsalba


The main module behind fishtank.py.
"""


import os
import sys
from typing import Optional, Union
from pytermgui.utils import hide_cursor, wipe

from . import __version__, usage_data, dbg, to_local
from .interface import InterfaceManager
from .layout_generators import generate
from .fish_generator import generate_fish


# pylint: disable=unused-argument
def exit_program() -> None:
    """Exit program in a clean manner"""

    hide_cursor(0)
    wipe()
    sys.exit(0)


# pylint: disable=invalid-name
def main() -> None:
    """main method"""

    if not os.path.isfile(to_local("fish_types.py")):
        print("generating")
        generate_fish(to_local("data/species.json"))

    open(to_local("log"), "w").close()
    generate(output=dbg)
    dbg("starting interface...")
    InterfaceManager().start()

    dbg("thats all folks!")
    exit_program()


def test_args(
    short: str, long: str, args: list[str], return_index: Optional[bool] = False
) -> Optional[Union[bool, int]]:
    """Return if either short or long is in args"""

    for i, opt in enumerate(args):
        if opt in [long, short]:
            if return_index:
                return i

            return True

    if return_index:
        return None

    return False


def cmdline() -> None:
    """Function to handle command line calling"""

    args = sys.argv[1:]

    if len(args) == 0:
        main()
        sys.exit(0)

    elif test_args("-h", "--help", args):
        print(usage_data)
        sys.exit(0)

    elif test_args("-g", "--generate-layouts", args):
        generate(output=print)
        sys.exit(0)

    elif (
        index := test_args("-fg", "--generate-fish", args, return_index=True)
    ) is not None:
        if not index + 1 < len(args):
            print("Not enough arguments!")
            sys.exit(1)

        generate_fish(args[index + 1])

    elif (index := test_args("", "--benchmark", args, return_index=True)) is not None:
        num = None
        if index + 1 < len(args):
            try:
                num = int(args[index + 1])
            except TypeError:
                print("Argument to --benchmark has to be an integer!")
                sys.exit(1)

        InterfaceManager().benchmark(num)

    else:
        print("not sure what to do with", args)


if __name__ == "__main__":
    main()
