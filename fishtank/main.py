"""
fishtank.main
-------------
author: bczsalba


The interface to the interactive fishtank to your terminal.
"""


from sys import exit
from math import sqrt
from time import sleep
from typing import Union
from random import randint
from signal import signal, SIGINT

from pytermgui import gradient, real_length
from pytermgui import Container, BaseElement, padding_label
from pytermgui.utils import hide_cursor, width, height, wipe
from . import SPECIES_DATA



class Position:
    """ Class for easier & more legible positions """

    # pylint: disable=invalid-name
    def __init__(self, x: int = 0, y: int = 0, xy: list[int, int] = None):
        if xy:
            self.x, self.y = xy
        else:
            self.x = x
            self.y = y

    def __eq__(self, other: "Position") -> bool:
        """ Return if two Position objects are equal """

        return self.x == other.x and self.y == other.y

    def __add__(self, other: "Position") -> "Position":
        """ Return new Position containing added values """

        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Position") -> "Position":
        """ Return new Position contianing substracted values """

        return Position(self.x - other.x, self.y - other.y)

    def __repr__(self) -> str:
        """ Return string of self """

        return f"Position({self.x},{self.y})"

    def __iter__(self) -> int:
        """ Yield values of self.x, self.y; allows: x, y = Position()         """

        for v in self.x, self.y:
            yield v

    def __bool__(self) -> bool:
        return True

    def show(self) -> str:
        """ Return 'x' at the position of self """

        return f"\033[{self.y};{self.x}Hx"

    def distance_to(self, other) -> float:
        """ Return distance from self to other """

        return sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)

class Fish:
    r"""
    <>< Fish class ><>

     ________school_________
    |                 ><>   |
    |       ><>             |
    |   ><>       ><>    A  |
    | |∧.__  |∧/__    __'V  |
    | \A| |  \A| |    | |A  |
    -------------------------

    - Aquarium()
    """

    # pylint: disable=too-many-instance-attributes, invalid-name
    def __init__(
        self,
        pos: list[int, int],
        species: str = "Molly",
        name: str = None,
        age: int = 0,
    ):
        """ Set up instance """

        # set up default values that are set during _load_from, so pylint doesn't yell at us.
        self.parent = None
        self.pigment = []
        self.stages = []
        self.path = []
        self.speed = 1
        self.skin = ""

        # assign species data
        assert species in SPECIES_DATA.keys()
        self.species = species

        _species_data = SPECIES_DATA.get(species)
        self._load_from(_species_data)

        # assign overwrites if name given
        if name:
            special_data = _species_data["specials"].get(name)

            if special_data:
                self._load_from(special_data)
                self.name = name
        else:
            self.name = None

        # delete large dictionary from memory
        del _species_data
        self.age = age

        # 0 -> left, 1 -> right
        self._heading = 0
        self._pos = None

        self.pos = Position(xy=pos)
        self.tank = None

        repr(self)

    @staticmethod
    def _reverse_skin(skin) -> str:
        """ Return char by char reversed version of skin """

        rev = ""
        reversible = ["<>", "[]", "{}", "()", "/\\", "db", "qp"]
        for c in reversed(skin):
            for r in reversible:
                if c in r:
                    new = r[r.index(c) - 1]
                    break
            else:
                new = c

            rev += new

        return rev

    @property
    def bounds(self) -> tuple[int, int, int, int]:
        """ Return boundaries of object """

        x, y = self.pos
        return x, y, x + real_length(self.skin), y

    @property
    def pos(self):
        """ Getter of _pos """

        return self._pos

    @pos.setter
    def pos(self, new):
        """ Update the fish's position """

        if self._pos:
            px, _ = self._pos
            x, _ = new

        self._pos = new

    def __repr__(self) -> str:
        """ __repr__ method that handles pigmenting """

        _skin = self.stages[self.age]
        self.skin = _skin

        if self._heading:
            skin = self._reverse_skin(_skin)
            pigment = list(reversed(self.pigment))

        else:
            skin = _skin
            pigment = self.pigment

        return gradient(skin, pigment)

    def _load_from(self, data: dict) -> None:
        """ Set self data from data """

        for key, value in data.items():
            if not key == "specials":
                setattr(self, key, value)

    def get_path(self, pos: Position) -> list[Position]:
        """ Get position to pos, return it as a list of Position-s """

        x1, y1 = self.pos
        x2, y2 = pos

        if x1 > x2:
            self._heading = 1
        else:
            self._heading = 0

        # x dif, x direction
        dx = abs(x2 - x1)
        sx = 1 if x1 < x2 else -1

        # y dif, y direction
        dy = -abs(y2 - y1)
        sy = 1 if y1 < y2 else -1

        # error
        error = dx + dy

        path = []
        while True:
            pos = Position(x1, y1)
            skin_end = Position(x1 + real_length(self.skin), y1)

            if (
                self.parent is not None
                and not self.parent.contains(pos)
                or not self.parent.contains(skin_end)
            ):
                break

            path.append(pos)
            if x1 == x2 and y1 == y2:
                break

            error2 = 2 * error

            if error2 >= dy:
                error += dy
                x1 += sx

            if error2 <= dx:
                error += dx
                y1 += sy

        return path

    def update(self) -> Position:
        """ Do next position update """

        if len(self.path) > 0:
            self.pos = self.path[0]
            self.path.pop(0)

        else:
            self.path = self.get_path(self.parent.get_next_position())
            self.parent.target_pos = None
            self.update()

        return self.pos

    def wipe(self) -> None:
        """ Wipe fish's skin at its current position """

        x, y = self.pos
        print(f"\033[{y};{x}H" + real_length(self.skin) * " ")

    def show(self) -> None:
        """ Show repr(self) at self.pos """

        x, y = self.pos
        print(f'\033[{y};{x}H'+repr(self))

class Aquarium(Container):
    """ An object to store & update fish """

    # pylint: disable=invalid-name
    def __init__(
        self, pos: list[int, int] = None, _width: int = 100, _height: int = 30
    ):
        """ Set up object """
        super().__init__(width=_width, height=_height)

        self.fish = []
        if pos is None:
            pos = [0, 0]

        x, y = pos
        self.pos = Position(x, y)

        for _ in range(self.height):
            self += padding_label

        repr(self)
        self.center()

        self.target_pos = None

    @property
    def bounds(self) -> tuple[int, int, int, int]:
        """ Return boundaries of object """

        x, y = self.pos
        return x + 1, y + 1, x + self.width - 1, y + self.height - 1

    def __iter__(self) -> Fish:
        """ Iterate through fish children """

        for fish in self.fish:
            yield fish

    def __add__(self, other: Union[BaseElement, Fish]) -> "self":
        """ Add BaseElement or Fish to contents """

        if issubclass(type(other), BaseElement):
            self._add_element(other)
        else:
            self.fish.append(other)
            if not self.contains(other.pos):
                other.pos = self.pos + Position(5, 5)
            other.parent = self

        return self

    def __iadd__(self, other: Union[BaseElement, Fish]) -> "self":
        """ Execute __add__, return self """

        return self.__add__(other)

    def _get_position_in_bounds(self) -> Position:
        """ Return a Position() object that is guaranteed to be within bounds """

        startx, starty, endx, endy = self.bounds
        return Position(randint(startx, endx), randint(starty, endy))

    def is_filled(self, pos: Position) -> bool:
        """ Return the thing that is at the position given """

        px, py = pos
        for e in self.fish:
            startx, starty, endx, endy = e.bounds
            if starty <= y <= endy and startx <= x <= endx:
                return e

        return None

    def contains(self, pos: Position) -> bool:
        """ Return if position is contained within self """

        x, y = pos
        startx, starty, endx, endy = self.bounds
        return startx < x < endx and starty < y < endy

    def move(self, pos: list[int, int], _wipe: bool = False) -> None:
        """ Implement move method using Position-s """

        self.pos = Position(xy=pos)
        if _wipe:
            self.wipe()
        self.get_border()

        return self

    def get_next_position(self) -> Position:
        """ Return a target position for fish """

        if self.target_pos is None:
            self.target_pos = self._get_position_in_bounds()

        return self.target_pos

    def update(self):
        """ Update all fish in self.fish """

        for fish in self.fish:
            fish.wipe()
            fish.update()
            fish.show()



def exit_program(sig, frame):
    hide_cursor(0)
    wipe()
    exit(0)


# pylint: disable=invalid-name
def main():
    """
    main method

    testing purposes, for now.
    """

    wipe()
    signal(SIGINT, exit_program)
    current_aquarium = Aquarium([0, 0])  # , _width=30, _height=10)
    print(current_aquarium)

    g = Fish([10, 0], name="goldie")
    m = Fish([10, 0], name="mjoofin")
    w = Fish([10, 0], name="winona")

    m.age = 2
    g.age = 2
    w.age = 1

    for f in [g, m, w]:
        current_aquarium += Fish([10, 0], name="mjoofin", age=2)
        current_aquarium += Fish([10, 0], name="goldie", age=2)
        current_aquarium += Fish([10, 0], name="jumbo", age=2)
        current_aquarium += Fish([10, 0], name="winona", age=2)

    hide_cursor()

    # main loop
    while True:
        current_aquarium.update()
        sleep(1 / 30)

    exit_program('','')


if __name__ == "__main__":
    main()
