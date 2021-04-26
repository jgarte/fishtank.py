"""
fishtank.main
-------------
author: bczsalba


The main module behind fishtank.py.
"""


import sys
from pytermgui.utils import hide_cursor, wipe

from . import interface, __version__, usage_data, dbg
from .layout_generators import generate


# pylint: disable=unused-argument
def exit_program(sig, frame):
    """ Exit program in a clean manner """

    hide_cursor(0)
    wipe()
    sys.exit(0)


# pylint: disable=invalid-name
def main():
    """ main method """

    # dbg('generating layouts..')
    generate(mode="dbg")
    # dbg('done!')

    dbg("starting interface...")
    interface.InterfaceManager().start()

    dbg("thats all folks!")
    exit_program("", "")


def test_args(short: str, long: str, args: list):
    """ Return if either short or long is in args """

    return any(opt in args for opt in [short, long])


def cmdline():
    """ Function to handle command line calling """

    args = sys.argv[1:]

    if len(args) == 0:
        sys.exit(main())

    elif test_args("-h", "--help", args):
        print(usage_data)
        sys.exit(0)

    elif test_args("-g", "--generate-layouts", args):
        sys.exit(generate(mode="print"))

    else:
        print("not sure what to do with", args)


if __name__ == "__main__":
    main()
