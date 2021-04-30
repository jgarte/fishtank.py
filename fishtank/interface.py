"""
fishtank.interface
------------------
author: bczsalba


The interface to the interactive fishtank to your terminal.
"""
# pylint: disable=too-many-instance-attributes

from __future__ import annotations

from typing import Type
from threading import Thread
from random import randint
from time import sleep

from pytermgui import (
    BaseElement,
    Container,
    Prompt,
    Label,
    padding_label,
    getch,
    color,
    clean_ansi,
    load_from_file,
)
from pytermgui.utils import (
    keys,
    basic_selection,
    hide_cursor,
    wipe,
    width,
    height,
)

from .classes import Fish, Aquarium, Position, Food
from . import SPECIES_DATA, to_local, styles, dbg
from .enums import FishProperties, FishType


class Menu:
    """ Boilerplate class for menus """

    def __init__(self, interface: InterfaceManager):
        """ Stub for init """

        self.interface = interface
        self.setup()
        self.run()

    def setup(self) -> None:
        """ Stub for menu setup """

    def run(self) -> None:
        """ Stub for menu run """


# pylint: disable=fixme,unreachable,E1123,E1123,E1121,E1101,R0201,E1120
# TODO: this needs to be rewritten, ^ is ugly as hell.
class NewfishDialog(Menu):
    """ Menu for creating a new ><> """

    def setup(self) -> None:
        """ Create objects & variables """

        return
        self.types = list(SPECIES_DATA.keys())
        self.age_names = ["fry", "juvenile", "adult"]

        self.menu = load_from_file(to_local("layouts/newfish.ptg"))
        self.showcase_fish = Fish(self.interface.aquarium, keep_data=True)
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
            "short_highlight", lambda depth, item: color(clean_ansi(item), 67)
        )

        self.current_index = 0
        self.fish_key = self.types[self.current_index]

        self.variants.value = list(SPECIES_DATA[self.fish_key]["variants"])[0]
        self.age.value = self.age_names[1]

        self.skin.set_style("value", self.get_skin)
        self.update_fish()
        self.menu.select()
        print(self.menu.center())

    # pylint: disable=unused-argument
    def get_skin(self, depth: int, value: str) -> str:
        """ Return skin of currently selected fish species """

        return ""
        return repr(self.showcase_fish)

    def update_fish(self) -> None:
        """ Update showcase fish pigment & skin """

        return

        fish = self.showcase_fish
        fish.species = self.fish_key
        fish.variant = self.variants.value
        fish.name = self.name.value
        fish.age = self.age_names.index(self.age.value)
        fish.pigment = fish.get_pigment(fish.species_data)

    def change_name(self, caller: Type[BaseElement]) -> None:
        """ Dialog to change the name of the fish """

        return
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

    def show_info(self, caller: Type[BaseElement]) -> None:
        """ Show information (stats) about a fish species """

        return
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

    def choose_variant(self, caller: Type[BaseElement]) -> None:
        """ Allow user to choose from variants """

        return
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

    def choose_age(self, caller: Type[BaseElement]) -> None:
        """ Allow user to choose age """

        return
        cont = Container(width=40)
        cont += Label("Choose age for your fish!")
        cont += padding_label
        cont += Prompt(options=self.age_names)
        cont.center()

        basic_selection(cont, True)
        self.age.value = cont.selected[0].value

    def create_fish(self, caller: Type[BaseElement]) -> None:
        """ Create a new fish """

        return
        if not self.name.value == "None":
            properties = {
                "name": self.name.value,
                "species": self.fish_key,
                "age": self.age_names.index(self.age.value),
                "variant": self.variants.value,
            }

            aquarium = self.interface.aquarium
            aquarium += Fish(parent=aquarium, properties=properties)

            del self.showcase_fish

        else:
            self.interface.aquarium += self.showcase_fish
            del self.showcase_fish.species_data

    def run(self) -> None:
        key = ""
        return
        while key not in ["ESC", "SIGTERM"]:
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

                self.update_fish()

            self.menu.select()
            self.tabbar.select(self.current_index)
            self.fish_key = self.types[self.current_index]

            if _fish_change:
                self.variants.value = list(SPECIES_DATA[self.fish_key]["variants"])[0]
                self.update_fish()

            print(self.menu)


class FeedingMenu(Menu):
    """ Menu for feeding stuff """

    def setup(self) -> None:
        """ Set up values """

        self.pos = Position()

    def select(self) -> None:
        """ Show selection menu """

        key = ""

        right_pos = Position(1, 0)
        left_pos = Position(-1, 0)
        up_pos = Position(0, 1)
        down_pos = Position(0, -1)

        for obj in self.interface.aquarium:
            obj.show()

        while key not in ["ESC", "SIGTERM"]:
            key = getch()

            self.pos.wipe()
            if key in keys.prev:
                self.pos += up_pos

            elif key in keys.next:
                self.pos += down_pos

            elif key in keys.back:
                self.pos += left_pos

            elif key in keys.fore:
                self.pos += right_pos

            elif key == "ENTER":
                break

            for obj in self.interface.aquarium:
                obj.show()

            self.pos.show()

    def choose_size(self) -> None:
        """ not sure bout this one """

    def finish(self) -> None:
        """ Finalize & add """

        aquarium = self.interface.aquarium
        food = Food(aquarium, pos=self.pos)
        food.pos = self.pos

        aquarium += food

    def run(self) -> None:
        """ Run menu """

        self.select()
        self.choose_size()
        self.finish()


class InterfaceManager:
    """ Manager class for all interface related operations """

    def __init__(self) -> None:
        styles.default()

        self.aquarium: Aquarium = Aquarium(_width=width()//2, _height=height()-15)
        self.aquarium.fps: int = 25
        self.aquarium.center()

        self._loop = True
        self._display_loop = Thread(target=self.display_loop, name="display_loop")

    def display_loop(self) -> None:
        """ Main display loop """

        print(self.aquarium)
        while self._loop:
            self.aquarium.update()
            sleep(1 / 25)

    def getch_loop(self) -> None:
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
                self.aquarium.pause(False)

            elif key == "f":
                self.aquarium += Food(self.aquarium)
                # currently unused
                # self.show(FeedingMenu)

            elif key == "*":
                properties = self.generate_fish_properties()
                self.aquarium += Fish(self.aquarium, properties)

            elif key == "CTRL_R":
                self.aquarium.objects = []
                self._loop = False
                self._display_loop.join()
                self._display_loop = Thread(target=self.display_loop)
                self._loop = True
                self.start()

            elif key == "CTRL_L":
                wipe()
                print(self.aquarium)

    def show(self, menu: Type[Menu]) -> None:
        """ Show menu object """

        wipe()
        self.aquarium.pause()

        menu(self)

        wipe()
        self.aquarium.pause(False)

    def generate_fish_properties(self) -> FishProperties:
        """ Generate random fish properties """

        def get_random_from_generator(values: set[str]) -> str:
            """ Helper for getting random items """

            items = list(values)
            start = 0
            end = len(items) - 1

            return items[randint(start, end)]

        data = SPECIES_DATA

        species = get_random_from_generator(data.keys())
        variant = get_random_from_generator(data[species]["variants"].keys())

        # this step could/should be automated
        stages = data[species]["stages"]
        _type = data[species]["type"]

        if _type == "top_dweller":
            _type = FishType.TOP_DWELLER

        elif _type == "mid_water":
            _type = FishType.MID_WATER

        elif _type == "bottom_dweller":
            _type = FishType.BOTTOM_DWELLER

        output: FishProperties = {
            "pos": [0, 0],
            "species": species,
            "stages": stages,
            "type": _type,
            "variant": variant,
            "name": "test",
            "age": 0,
        }

        return output

    def start(self) -> None:
        """ Main loop of the program """

        wipe()
        hide_cursor()

        for _ in range(20):
            properties = self.generate_fish_properties()
            self.aquarium += Fish(self.aquarium, properties)

        self._display_loop.start()
        self.getch_loop()
