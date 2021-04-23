"""
fishtank.main
-------------
author: bczsalba


The interface to the interactive fishtank to your terminal.
"""


from math import sqrt
from time import sleep
from typing import Union
from random import randint

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

    def __eq__(self, other: 'Position') -> bool:
        """ Return if two Position objects are equal """

        return self.x == other.x and self.y == other.y

    def __add__(self, other: 'Position') -> 'Position':
        """ Return new Position containing added values """

        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Position') -> 'Position':
        """ Return new Position contianing substracted values """

        return Position(self.x - other.x, self.y - other.y)

    def __repr__(self) -> str:
        """ Return string of self """

        return f'Position({self.x},{self.y})'

    def __iter__(self) -> int:
        """ Yield values of self.x, self.y; allows: x, y = Position()         """

        for v in self.x, self.y:
            yield v

    def show(self) -> str:
        """ Return 'x' at the position of self """

        return f'\033[{self.y};{self.x}Hx'

    def distance_to(self, other) -> float:
        """ Return distance from self to other """

        return sqrt((other.x - self.x)**2 + (other.y - self.y)**2)

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
    def __init__(self, pos: list[int, int], species: str = "Molly", name: str = None):
        """ Set up instance """

        # set up default values that are set during _load_from, so pylint doesn't yell at us.
        self.parent  = None
        self.pigment = []
        self.stages  = []
        self.speed   = 1
        self.skin    = ''
        self.age     = 0

        # assign species data
        assert species in SPECIES_DATA.keys()
        self.species = species

        _species_data = SPECIES_DATA.get(species)
        self._load_from(_species_data)

        # assign overwrites if name given
        if name:
            special_data = _species_data['specials'].get(name)

            if special_data:
                self._load_from(special_data)
                self.name = name
        else:
            self.name = None

        # delete large dictionary from memory
        del _species_data

        # 0 -> left, 1 -> right
        self._heading = 0
        self._pos = None

        self.pos = Position(xy=pos)
        self.tank = None

        repr(self)


    @staticmethod
    def _reverse_skin(skin) -> str:
        """ Return char by char reversed version of skin """

        rev = ''
        reversible = ['<>', '[]', '{}', '()', '/\\', 'db', 'qp']
        for c in reversed(skin):
            for r in reversible:
                if c in r:
                    new = r[r.index(c)-1]
                    break
            else:
                new = c

            rev += new

        return rev


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

            if x > px:
                self._heading = 0
            else:
                self._heading = 1

        self._pos = new


    def __repr__(self) -> str:
        """ __repr__ method that handles pigmenting & directioning """

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
            if not key == 'specials':
                setattr(self, key, value)


    def get_path(self, pos: Position) -> list[Position]:
        """ Get position to pos, return it as a list of Position-s """

        x1, y1 = self.pos
        x2, y2 = pos

        # x dif, x direction
        dx = abs(x2-x1)
        sx = (1 if x1 < x2 else -1)

        # y dif, y direction
        dy = -abs(y2-y1)
        sy = (1 if y1 < y2 else -1)

        # error
        error = dx+dy

        path = []
        while True:
            pos = Position(x1,y1)
            if self.parent is not None and not self.parent.contains(pos):
                break
 
            path.append(pos)
            if (x1 == x2 and y1 == y2):
                break

            error2 = 2*error

            if error2 >= dy:
                error += dy
                x1 += sx

            if error2 <= dx:
                error += dx
                y1 += sy

        return path


    def wipe(self) -> None:
        """ Wipe fish's skin at its current position """

        x, y = self.pos
        print(f'\033[{y};{x}H'+real_length(self.skin)*' ')

class Aquarium(Container):
    """ An object to store & update fish """

    # pylint: disable=invalid-name
    def __init__(self, pos: list[int, int] = None, _width: int = 100, _height: int = 30):
        """ Set up object """
        super().__init__(width=_width, height=_height)

        self.fish = []
        if pos is None:
            pos = [0,0]

        x, y = pos
        self.pos  = Position(x, y)

        for _ in range(self.height):
            self += padding_label

        repr(self)
        self.pos = Position((width()-x-self.width)//2, (height()-y-self.height)//2)

    def __iter__(self) -> Fish:
        """ Iterate through fish children """

        for fish in self.fish:
            yield fish

    def __add__(self, other: Union[BaseElement, Fish]) -> 'self':
        """ Add BaseElement or Fish to contents """

        if issubclass(type(other), BaseElement):
            self._add_element(other)
        else:
            self.fish.append(other)
            other.parent = self

        return self

    def __iadd__(self, other: Union[BaseElement, Fish]) -> 'self':
        """ Execute __add__, return self """

        return self.__add__(other)

    def contains(self, pos: Position) -> bool:
        """ Return if position is contained within self """

        x, y = pos
        startx, starty = self.pos
        startx += 1
        starty += 1

        endx = startx + self.width - 2
        endy = starty + self.height - 2

        return startx < x < endx and starty < y < endy









# pylint: disable=invalid-name
def main():
    """ 
    main method 

    testing purposes, for now.
    """

    a = Aquarium([0,0])
    print(a)

    m = Fish([10, 0], name="mjoofin")
    a += m
    m.pos = a.pos + Position(5,5)

    hide_cursor()
    while True:
        wipe()
        target = m.pos + Position(randint(-width(),width()), randint(-height(), height()))
        print('moving to:', target)
        print(a)

        for pos in m.get_path(target):
            m.wipe()
            m.pos = pos
            x, y = pos

            print(f'\033[{y};{x}H'+repr(m))
            sleep(1/60 * m.speed)

    hide_cursor(0)


if __name__ == "__main__":
    main()
