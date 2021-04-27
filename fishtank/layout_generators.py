"""
fishtank.layout_generators
--------------------------
author: bczsalba


This module generates the .ptg files used in the program's UI.

It is run at every startup, but can be called manually: `fishtank --generate-layouts`
"""

from os import mkdir
from os.path import abspath, isdir

from pytermgui.utils import width
from pytermgui import (
    Container,
    Prompt,
    Label,
    InputField,
    padding_label,
    dump_to_file,
)

from . import to_local, dbg


def generate_newfish_dialog() -> None:
    """ Menu for creating a new fish """

    cont = Container(width=32, shorten_elements=False)

    cont.static_width = 32
    cont += Label("add new fish!")
    cont += padding_label

    tank = Container(width=11)
    tank.static_width = 12

    skin = Label("")
    skin.id = "label_skin"
    tank += skin

    cont += tank
    cont += padding_label

    data = Container(shorten_elements=False)

    p_name = Prompt("name:", "None")
    p_name.id = "prompt_name"
    data += p_name

    p_age = Prompt("age:", "None")
    p_age.id = "prompt_age"
    data += p_age

    p_variants = Prompt("variant:", "None")
    p_variants.id = "prompt_variants"
    data += p_variants

    p_info = Prompt("info:", "-> {}")
    p_info.id = "prompt_info"
    data += p_info

    data.static_width = 24
    cont += data

    button = Prompt(options=["add!"])
    button.id = "prompt_button"
    cont += padding_label
    cont += button
    cont += padding_label

    tabbar = Prompt(options=["none"])
    tabbar.is_selectable = False
    tabbar.id = "prompt_tabbar"
    cont += tabbar

    data.set_style(Prompt, "delimiter_chars", lambda: None)
    cont.set_style(Prompt, "delimiter_chars", lambda: "<>")

    dump_to_file(cont, to_local("layouts/newfish.ptg"))


def generate_input_dialog() -> None:
    """ General dialog containing an InputField """

    cont = Container(width=width(), border=lambda: " -")

    title = Label("placeholder_title")
    title.id = "label_title"
    cont += title
    cont += padding_label
    cont += padding_label

    infield = InputField(padding=1, print_at_start=False)
    infield.id = "inputfield_input"
    cont += infield

    dump_to_file(cont, to_local("layouts/input_dialog.ptg"))


def generate_info_page() -> None:
    """ Read-only information display """

    cont = Container()
    cont.static_width = 50
    title = Label("placeholder_title")
    title.id = "label_title"

    cont += title
    cont += padding_label

    inner = Container()
    inner.id = "container_inner"
    cont += inner

    dump_to_file(cont, to_local("layouts/info_page.ptg"))


def generate(mode: str = "print") -> None:
    """ Run all generators """

    if not isdir(to_local("layouts")):
        mkdir(abspath(to_local("layouts")))

    for key, value in globals().items():
        if callable(value) and key.startswith("generate_"):
            text = f"Running {key}() ... "

            if mode == "print":
                print(text, end="", flush=True)

            value()

            if mode == "print":
                print("done!")
            else:
                dbg(text + "done!")
