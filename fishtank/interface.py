"""
fishtank.interface
------------------
author: bczsalba


The interface to the interactive fishtank to your terminal.
"""
# pylint: disable=too-many-instance-attributes

from __future__ import annotations

from threading import Thread
from time import time, sleep
from typing import Type

from pytermgui import (
    BaseElement,
    Container,
    Prompt,
    Label,
    padding_label,
    styles,
    getch,
    color,
    gradient,
    clean_ansi,
    load_from_file,
)
from pytermgui.utils import keys, basic_selection, hide_cursor, wipe

from . import SPECIES_DATA, to_local
from .classes import Fish, Aquarium


class Menu:
    """ Boilerplate class for menus """

    def __init__(self, interface: InterfaceManager):
        """ Stub for init """

        self.interface = interface
        self.setup()
        self.run()

    def setup(self):
        """ Stub for menu setup """

    def run(self):
        """ Stub for menu run """


class NewfishDialog(Menu):
    """ Menu for creating a new ><> """

    def setup(self):
        """ Create objects & variables """

        self.types = list(SPECIES_DATA.keys())
        self.age_names = ["fry", "juvenile", "adult"]

        self.menu = load_from_file(to_local("layouts/newfish.ptg"))
        tank = self.menu[2]
        box = self.menu[4]

        self.skin = tank.get_object_by_id("label_skin")
        self.name = box.get_object_by_id("prompt_name")
        self.info = box.get_object_by_id("prompt_info")
        self.age = box.get_object_by_id("prompt_age")
        self.variants = box.get_object_by_id("prompt_variants")
        self.tabbar = self.menu.get_object_by_id("prompt_tabbar")
        self.button = self.menu.get_object_by_id("prompt_button")

        self.name.submit = self.change_name
        self.info.submit = self.show_info
        self.age.submit = self.choose_age
        self.button.submit = self.create_fish
        self.variants.submit = self.choose_variant

        self.tabbar.options = self.types
        self.tabbar.select()
        self.tabbar.set_style(
            "short_highlight", lambda depth, item: color(clean_ansi(item), 210)
        )

        self.current_index = 0
        self.fish_key = self.types[self.current_index]

        self.variants.value = list(SPECIES_DATA[self.fish_key]["variants"])[0]
        self.age.value = self.age_names[1]

        self.skin.set_style("value", self.get_skin)
        self.menu.select()
        print(self.menu.center())

    # pylint: disable=unused-argument
    def get_skin(self, depth: int, value: str):
        """ Return skin of currently selected fish species """

        data = SPECIES_DATA[self.fish_key]
        return gradient(data["stages"][1], data["pigment"])

    def change_name(self, caller: Type[BaseElement]):
        """ Dialog to change the name of the fish """

        self.menu.wipe()
        dialog = load_from_file(to_local("layouts/input_dialog.ptg"))
        dialog.center()

        title = dialog.get_object_by_id("label_title")
        title.value = "name your fish!"
        field = dialog.get_object_by_id("inputfield_input")
        field.value = self.name.value
        field.cursor = len(self.name.value) + 1

        print(dialog)

        key = ""
        while key not in ["SIGTERM", "ESC"]:
            key = getch()

            if key == "ENTER":
                self.name.value = field.value
                break

            field.send(key)

            field.wipe()
            print(field)

        dialog.wipe()

    def show_info(self, caller: Type[BaseElement]):
        """ Show information (stats) about a fish species """

        self.menu.wipe()
        data = SPECIES_DATA[self.fish_key]

        data = {
            "name": self.fish_key,
            "speed": str(data["speed"]),
            "variants": str(len(data["variants"])),
        }

        page = load_from_file(to_local("layouts/info_page.ptg"))
        title = page.get_object_by_id("label_title")
        inner = page.get_object_by_id("container_inner")

        title.value = f"information about {self.fish_key}"
        for key, value in data.items():
            inner += Prompt(key, value)
            inner[-1].is_selectable = False

        print(page.center())

        while True:
            if getch() == "ESC":
                break
        page.wipe()

    def choose_variant(self, caller: Type[BaseElement]):
        """ Allow user to choose from variants """

        cont = Container(width=40)
        cont.static_width = 40
        variants = SPECIES_DATA[self.fish_key]["variants"]
        cont += Label(f"Choose {self.fish_key} variant")
        cont += padding_label

        inner = Container()
        inner.static_width = 34
        for var in variants.keys():
            inner += Prompt(options=[var])

        cont += inner
        cont.center()

        basic_selection(cont, True)
        self.variants.value = inner.selected[0].real_value

    def choose_age(self, caller: Type[BaseElement]):
        """ Allow user to choose age """

        cont = Container(width=40)
        cont += Prompt(options=self.age_names)

        basic_selection(cont, True)
        self.age.value = cont.selected[0].value

    def create_fish(self, caller: Type[BaseElement]):
        """ Create a new fish """

        properties = {
            "name": self.name.value,
            "species": self.fish_key,
            "age": self.age_names.index(self.age.value),
            "variant": self.variants.value,
        }

        aquarium = self.interface.aquarium
        aquarium += Fish(parent=aquarium, properties=properties)

    def run(self):
        key = ""
        while key not in ["SIGTERM", "ESC"]:
            _fish_change = False
            key = getch()

            if key in keys.prev:
                self.menu.selected_index -= 1

            elif key in keys.next:
                self.menu.selected_index += 1

            elif key in keys.back:
                self.current_index = max(self.current_index - 1, 0)
                _fish_change = True

            elif key in keys.fore:
                self.current_index = min(self.current_index + 1, len(self.types) - 1)
                _fish_change = True

            elif key == "ENTER":
                self.menu.wipe()
                self.menu.submit()

                if self.menu.selected[0] == self.button:
                    break

            self.menu.select()
            self.tabbar.select(self.current_index)
            self.fish_key = self.types[self.current_index]

            if _fish_change:
                self.variants.value = list(SPECIES_DATA[self.fish_key]["variants"])[0]
            print(self.menu)


class InterfaceManager:
    """ Manager class for all interface related operations """

    def __init__(self):
        styles.draculite()
        self.aquarium = Aquarium()

        self._loop = True
        self._display_loop = Thread(target=self.display_loop)

    def display_loop(self):
        """ Main display loop """

        print(self.aquarium)
        while self._loop:
            self.aquarium.update()
            print("\033[H" + str(time()))
            sleep(1 / 30)

    def getch_loop(self):
        """ Main input loop """

        while self._loop:
            key = getch()

            if key == "SIGTERM":
                self._loop = False
                hide_cursor(False)
                wipe()
                break

            if key == "+":
                self.show(NewfishDialog)

            elif key == " ":
                self.aquarium.pause()
                getch()
                self.aquarium.pause(0)

    def show(self, menu: Type[Menu]):
        """ Show menu object """

        wipe()
        self.aquarium.pause()

        menu(self)

        wipe()
        print(self.aquarium)
        self.aquarium.pause(False)

    def start(self):
        """ Method that starts Interface """

        wipe()
        hide_cursor()

        # x1, y1, x2, y2 = self.aquarium.bounds
        # from .classes import Position
        # print(self.aquarium)
        # print('\033[38;5;1m'+Position(x1,y1).show())
        # print('\033[38;5;1m'+Position(x2,y2).show())
        # print('\033[m')

        for _ in range(10):
            self.aquarium += Fish(self.aquarium)
        # self.aquarium += Fish(self.aquarium)
        # self.aquarium += Fish(self.aquarium)
        # self.aquarium += Fish(self.aquarium)
        self._display_loop.start()
        self.getch_loop()
