"""
fishtank.classes
----------------
author: bczsalba


File containing most classes.
"""

from __future__ import annotations

# pylint: disable=no-name-in-module
from math import sqrt
from random import randint
from typing import Union, Generator, Optional

from pytermgui import gradient, real_length, clean_ansi
from pytermgui import Container, BaseElement, padding_label

from . import SPECIES_DATA


class Position:
    """ Class for easier & more legible positions """

    # pylint: disable=invalid-name
    def __init__(self, x: int = 0, y: int = 0, xy: list[int] = None):
        if xy:
            self.x, self.y = xy
        else:
            self.x = x
            self.y = y

    def __eq__(self, other: object) -> bool:
        """ Return if two Position objects are equal """

        if not isinstance(other, Position):
            raise NotImplementedError()

        return self.x == other.x and self.y == other.y

    def __add__(self, other: object) -> Position:
        """ Return new Position containing added values """

        if not isinstance(other, Position):
            raise NotImplementedError()

        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: object) -> Position:
        """ Return new Position containing substracted values """

        if not isinstance(other, Position):
            raise NotImplementedError()

        return Position(self.x - other.x, self.y - other.y)

    def __repr__(self) -> str:
        """ Return string of self """

        return f"Position({self.x},{self.y})"

    def __iter__(self) -> Generator[int, None, None]:
        """ Yield values of self.x, self.y; allows: x, y = Position() """

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
    def __init__(self, parent: Aquarium, properties: Optional[dict] = None):
        """ Set up instance """

        default_properties = {
            "species": "Molly",
            "variant": None,
            "name": None,
            "pos": [0, 0],
            "age": 0,
        }

        if properties is None:
            properties = {}

        # set up default values that are set during _load_from, so pylint doesn't yell at us.
        self.parent: Aquarium = parent
        self.species: str = ""
        self.variant: str = ""
        self.pigment: list[int] = []
        self.stages: list[str] = []
        self.path: list[Position] = []
        self.speed: int = 1
        self.age: int = 1
        self.skin: str = ""

        # set up properties dict
        for key, value in default_properties.items():
            if not key in properties.keys():
                properties[key] = value

        # load default properties
        _species_data = SPECIES_DATA.get(properties.get("species"))
        self._load_from(_species_data)

        # load given property overwrites
        self._load_from(properties)

        # set variant to random if not given
        if not self.variant:
            variants = _species_data["variants"]
            if isinstance(variants, dict):
                number = randint(0, 100)

                for name, value in variants.items():
                    if not isinstance(value, dict):
                        continue

                    if number in range(value["chance"]):
                        self.variant = name
                        break

                del variants

        # get pigmentation
        self.pigment = self._get_pigment(_species_data)

        # assign overwrites if name given
        if properties["name"]:
            special_data = _species_data["specials"].get(properties["name"])

            if special_data:
                self._load_from(special_data)

        # delete unneeded data
        del _species_data

        # 0 -> left, 1 -> right
        self._heading = 0
        self._pos = None

        self.pos = Position(xy=properties["pos"])

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

    def _get_pigment(self, data: dict) -> list[int]:
        variant_data = data["variants"].get(self.variant)
        if variant_data:
            pigment = []
            available = variant_data.get("pigment")
            length = max(len(clean_ansi(l)) for l in self.stages)

            for _ in range(length):
                pigment.append(available[randint(0, len(available) - 1)])

            return pigment

        return self.pigment

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

        self._pos = new

    def __repr__(self) -> str:
        """ __repr__ method that handles pigmenting """

        _skin = self.stages[self.age]
        self.skin = _skin

        if self._heading:
            skin = self._reverse_skin(_skin)
            pigment = list(reversed(self.pigment[: len(skin) - 1]))

        else:
            skin = _skin
            pigment = self.pigment[: len(skin) - 1]

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
            # try to avoid moving to a position already occupied
            fish_at_pos = self.parent.fish_at(self.pos)
            if fish_at_pos and fish_at_pos is not self:
                return self.pos

            self.pos = self.path[0]
            self.path.pop(0)

        else:
            if randint(0, 10) < 4:
                self.path += [self.pos] * randint(2, 5)

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
        print(f"\033[{y};{x}H" + repr(self))


class Aquarium(Container):
    """ An object to store & update fish """

    # pylint: disable=invalid-name
    def __init__(self, pos: list[int] = None, _width: int = 70, _height: int = 15):
        """ Set up object """
        super().__init__(width=_width, height=_height)

        self.fish: list[Fish] = []

        if pos is None:
            pos = [0, 0]

        x, y = pos
        self.pos = Position(x, y)

        for i, c in enumerate("..''"):
            self.set_corner(i, c)

        for _ in range(self.height):
            self += padding_label

        repr(self)
        self.center()

        self.target_pos: Union[Position, None] = None
        self._is_paused = False

    @property
    def bounds(self) -> tuple[int, int, int, int]:
        """ Return boundaries of object """

        x, y = self.pos
        return x + 1, y + 1, x + self.width + 1, y + self.height

    def __iter__(self) -> Generator[Fish, None, None]:
        """ Iterate through fish children """

        for fish in self.fish:
            yield fish

    def __add__(self, other: Union[BaseElement, Fish]) -> Aquarium:
        """ Add BaseElement or Fish to contents """

        if issubclass(type(other), BaseElement):
            self._add_element(other)
        else:
            self.fish.append(other)
            if not self.contains(other.pos):
                other.pos = self._get_position_in_bounds(other)
            other.parent = self

        return self

    def __iadd__(self, other: Union[BaseElement, Fish]) -> Aquarium:
        """ Execute __add__, return self """

        return self.__add__(other)

    def _get_position_in_bounds(self, obj: Optional[Fish] = None) -> Position:
        """ Return a Position() object that is guaranteed to be within bounds """

        startx, starty, endx, endy = self.bounds

        if obj:
            startx += real_length(obj.skin)
            endx -= real_length(obj.skin)

        return Position(randint(startx + 1, endx - 1), randint(starty + 1, endy - 1))

    def pause(self, value: bool = True) -> None:
        """ Pause updates """

        self._is_paused = value

    def fish_at(self, pos: Position) -> Optional[Fish]:
        """ Return the thing that is at the position given """

        px, py = pos
        for e in self.fish:
            startx, starty, endx, endy = e.bounds
            if starty <= py <= endy and startx <= px <= endx:
                return e

        return None

    def contains(self, pos: Position) -> bool:
        """ Return if position is contained within self """

        x, y = pos
        startx, starty, endx, endy = self.bounds
        return startx < x < endx and starty < y < endy

    def move(self, pos: list[int], _wipe: bool = False) -> Aquarium:
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

        if self._is_paused:
            return

        for fish in self.fish:
            fish.wipe()
            fish.update()
            fish.show()