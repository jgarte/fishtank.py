"""
fishtank.classes
----------------
author: bczsalba


File containing most classes.
"""

from __future__ import annotations

# this import should fail according to pylint, but only on macos.
# pylint: disable=no-name-in-module
from math import sqrt
from random import randint
from typing import Union, Generator, Optional, Any

from pytermgui import gradient, real_length, clean_ansi
from pytermgui import Container, BaseElement, padding_label

# `dbg` is usually not used in pushed code, but is often called  otherwise.
# pylint: disable=unused-import
from . import SPECIES_DATA, dbg
from .enums import (
    Event,
    AquariumEvent,
    BoundaryError,
    FishType,
    FishProperties,
)


class Position:
    """ Class for easier & more legible positions """

    # having variables named x and y makes most sense
    # pylint: disable=invalid-name
    def __init__(self, x: int = 0, y: int = 0, xy: Optional[list[int]] = None):
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

    def __gt__(self, other: object) -> bool:
        """ Return if self.x > other.x """

        if not isinstance(other, Position):
            raise NotImplementedError()

        return self.x > other.x

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

    def show(self) -> None:
        """ Print self """

        print(f"\033[{self.y};{self.x}Hx")

    def wipe(self) -> None:
        """ Wipe character at self.x & self.y """

        print(f"\033[{self.y};{self.x}H ")

    def distance_to(self, other: object) -> float:
        """ Return distance from self to other """

        if not isinstance(other, Position):
            raise NotImplementedError()

        return sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)


class Boundary:
    """ Boundary made up by two Position objects, non-inclusive of borders """

    def __init__(self, pos1: Position, pos2: Position) -> None:
        """ Initialize object """

        self.start = pos1
        self.end = pos2

    def __iter__(self) -> Generator[int, None, None]:
        """ Iterate start and end positions """

        for pos in [self.start, self.end]:
            for coord in pos:
                yield coord

    def _contains_coordinates(self, other: Position) -> bool:
        """ Helper to get if self contains other """

        error = self.error(other)

        if error is None:
            return True

        return False

    def positions(self) -> Generator[Position, None, None]:
        """ Iterate positions """

        for pos in self.start, self.end:
            yield pos

    def error(self, other: Position) -> Optional[BoundaryError]:
        """ Get BoundaryError from other in self"""

        startx, starty = self.start
        endx, endy = self.end

        otherx, othery = other

        x_error = not startx < otherx < endx
        y_error = not starty < othery < endy

        if not x_error and not y_error:
            return None

        if x_error and y_error:
            return BoundaryError.XY

        if x_error:
            return BoundaryError.X

        return BoundaryError.Y

    def contains(self, other: Union[Boundary, Position]) -> bool:
        """ Return whether self contains other """

        if isinstance(other, Position):
            return self._contains_coordinates(other)

        pos1, pos2 = other.start, other.end
        return self._contains_coordinates(pos1) and self._contains_coordinates(
            pos2
        )


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

    # it makes sense for this class to have as many attributes as it does.
    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent: Aquarium, properties: FishProperties):
        """ Set up instance """

        self.path: list[Position] = []
        self.pigment: list[int] = []
        self.skin_length: int = 0
        self.stages: list[str]
        self.skin: str = ""
        self.pos: Position
        self.variant: str
        self.species: str
        self.age: int

        self._food: Optional[Food] = None
        self._heading: int = 0

        self.parent = parent
        self._set_properties(properties)
        self.pigment = self.get_pigment()

        self.heading_left = -1
        self.heading_right = 1

    def _set_properties(self, properties: FishProperties) -> None:
        for key, value in properties.items():
            if key == "pos":
                # this is a no-case, but mypy complains
                if not isinstance(value, list):
                    raise NotImplementedError()

                posx, posy = value
                value = Position(posx, posy)

            setattr(self, key, value)

    @staticmethod
    def _reverse_skin(skin: str) -> str:
        """ Return char by char reversed version of skin """

        reversed_skin = ""
        reversible = ["<>", "[]", "{}", "()", "/\\", "db", "qp"]
        for char in reversed(skin):
            for rev in reversible:
                if char in rev:
                    new = rev[rev.index(char) - 1]
                    break
            else:
                new = char

            reversed_skin += new

        return reversed_skin

    @property
    def bounds(self) -> tuple[int, int, int, int]:
        """ Return boundaries of object """

        posx, posy = self.pos
        return posx, posy, posx + real_length(self.skin), posy

    def __repr__(self) -> Any:
        """
        __repr__ method that handles pigmenting

        Note:
            pytermgui.gradient() and this function
            should return str, and will do so once
            I get around to the rewrite.
        """

        _skin = self.stages[self.age]
        self.skin = _skin
        self.skin_length = real_length(_skin)

        # skins are right-headed
        if self._heading is self.heading_left:
            skin = self._reverse_skin(_skin)
            pigment = list(reversed(self.pigment[: len(skin) - 1]))

        else:
            skin = _skin
            pigment = self.pigment[: len(skin) - 1]

        return gradient(skin, pigment)

    def _position_valid(self, pos: Position) -> bool:
        if self.parent is None:
            return False

        posx, posy = pos
        start_pos = Position(posx, posy)
        end_pos = Position(posx + real_length(self.skin), posy)

        start_error = self.parent.bounds.error(start_pos)
        end_error = self.parent.bounds.error(end_pos)

        if start_error is None and end_error is None:
            return True

        return False

    def get_pigment(self) -> list[int]:
        """ Get pigmentation using self.variant"""

        # this is ugly, but outsourcing it to a function would be uglier.
        variant_data = SPECIES_DATA[self.species]["variants"].get(self.variant)
        if variant_data:
            pigment = []
            available = variant_data.get("pigment")
            length = max(len(clean_ansi(l)) for l in self.stages)

            for _ in range(length):
                pigment.append(available[randint(0, len(available) - 1)])

            return pigment

        return self.pigment

    def get_path(self, pos: Position) -> list[Position]:
        """ Get position to pos, return it as a list of Position-s """

        startx, starty = self.pos
        endx, endy = pos

        # x dif, x direction
        diffx = abs(endx - startx)
        intbuff_x = 1 if startx < endx else -1

        # y dif, y direction
        diffy = -abs(endy - starty)
        intbuff_y = 1 if starty < endy else -1

        if intbuff_x == 1:
            self._heading = self.heading_right
        else:
            self._heading = self.heading_left

        # error
        error = diffx + diffy

        path = []
        while True:
            pos = Position(startx, starty)
            if not self._position_valid(pos):
                break

            path.append(pos)
            if startx == endx and starty == endy:
                break

            error2 = 2 * error

            if error2 >= diffy:
                error += diffy
                startx += intbuff_x

            if error2 <= diffx:
                error += diffx
                starty += intbuff_y

        return path

    def update(self) -> Position:
        """
        Do next position update

        rewrite this pls
        """
        # pylint: disable=too-many-branches

        # try to find food candidates
        if not self._food:
            candidates = []
            for food in self.parent.foods():
                if food.health > 0:
                    distance = self.pos.distance_to(food.pos)
                    candidates.append((distance, food))

            # only assign when there is a food available
            if len(candidates) > 0:
                if randint(0, 3) == 1:
                    candidates.sort(key=lambda value: value[0])
                    self._food = candidates[0][1]

        else:
            if self.pos.distance_to(self._food.pos) < self.skin_length + 1:
                self._food.health -= 1
                if randint(0, 10) == 1 and self.age < len(self.stages) - 1:
                    self.age += 1
                    if self.pos < self._food.pos:
                        self._heading = self.heading_right
                    else:
                        self._heading = self.heading_left

        if len(self.path) > 0:
            self.pos = self.path[0]

            if self._food:
                # this mechanic is interesting, but it breaks things.
                offset = (
                    -real_length(self.skin) if self.pos < self._food.pos else 1
                )
                self.path = self.get_path(self._food.pos + Position(offset, 0))

            if len(self.path) > 0:
                self.path.pop(0)

        else:
            if randint(0, 10) < 4:
                self.path += [self.pos] * randint(2, 5)

            else:
                self.path = self.get_path(self.parent.get_next_position())

                if self._food is None:
                    self.parent.notify(AquariumEvent.TARGET_REACHED, self)
                else:
                    self._food = None

                self.update()

        return self.pos

    def notify(self, event: Event, data: Optional[Any]) -> None:
        """ Notify fish of some event """

        if event == AquariumEvent.FOOD_DESTROYED:
            if data is not self._food:
                return

            if randint(0, 3) < 2:
                self.path = []
                self._food = None
                self.update()

    def wipe(self) -> None:
        """ Wipe fish's skin at its current position """

        posx, posy = self.pos
        print(f"\033[{posy};{posx}H" + real_length(self.skin) * " ")

    def show(self) -> None:
        """ Show repr(self) at self.pos """

        posx, posy = self.pos
        print(f"\033[{posy};{posx}H" + repr(self))


class Food:
    """ fud """

    # it makes sense for this class to have this many attributes.
    # pylint: disable=too-many-instance-attributes
    def __init__(
        self, parent: Aquarium, health: int = 5, pos: Optional[Position] = None
    ):
        """ Initialize object """

        self.skin: str = "#"
        self.path: list[Position] = []
        self.counter: int = 0
        self._is_stopped: bool = False
        self._idle_framecount: int = 0

        if pos is None:
            self.pos = Position()
        else:
            self.pos = pos

        self.health = health
        self.parent = parent

    def stop(self) -> None:
        """ Stop updates of object """

        self._is_stopped = True

    def destroy(self) -> None:
        """ Remove self from parent """

        self.wipe()
        self.parent.notify(AquariumEvent.FOOD_DESTROYED, self)

    def update(self) -> None:
        """ Update position & path"""

        # destroy at 0 health of when the object has been idle for 10 seconds
        if self.health <= 0 or self._idle_framecount >= self.parent.fps * 10:
            self.destroy()

        if self._is_stopped:
            self._idle_framecount += 1
            return

        # only update on every second frame
        self.counter += 1
        if self.counter < 3:
            return

        self.counter = 0

        x_change = randint(-1, 1)

        # this is a clumsy call
        target_pos = self.pos + Position(x_change, 1)
        error = self.parent.bounds.error(target_pos)

        # only move down if x is out of bounds
        if error is BoundaryError.X:
            self.pos += Position(0, 1)
            return

        # stop moving if y is out of bounds
        if error is BoundaryError.XY or error is BoundaryError.Y:
            self.stop()
            return

        # add target otherwise
        self.pos = target_pos

    def wipe(self) -> None:
        """ Clear char at pos """

        posx, posy = self.pos
        print(f"\033[{posy};{posx}H" + real_length(self.skin) * " ")

    def show(self) -> None:
        """ Print self to pos """

        posx, posy = self.pos
        print(f"\033[{posy};{posx}H" + self.skin)


# as long as pytermgui is not type this error would occur.
class Aquarium(Container):  # type: ignore[misc]
    """ An object to store & update fish """

    # pylint: disable=invalid-name
    def __init__(
        self,
        pos: Optional[list[int]] = None,
        _width: int = 70,
        _height: int = 25,
    ):
        """ Set up object """

        super().__init__(width=_width, height=_height)

        self.fps: int
        self.objects: list[Union[Fish, Food]] = []
        self.target_pos: Union[Position, None] = None
        self.bounds: Boundary = self._get_bounds()

        self._is_paused: bool = False
        self._target_reached: list[Fish] = []

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

    def _get_bounds(self) -> Boundary:
        """ Return boundaries of object """

        x, y = self.pos
        start = Position(x + 1, y + 1)
        end = Position(x + self.width + 1, y + self.height)

        return Boundary(start, end)

    def foods(self) -> Generator[Food, None, None]:
        """ Iterate through foods """

        for obj in self.objects:
            if isinstance(obj, Food):
                yield obj

    def fish(self) -> Generator[Fish, None, None]:
        """ Iterate through fish """

        for obj in self.objects:
            if isinstance(obj, Fish):
                yield obj

    def __iter__(self) -> Generator[Union[Fish, Food], None, None]:
        """ Iterate through fish children """

        for obj in self.objects:
            yield obj

    def __add__(self, other: Union[BaseElement, Fish]) -> Aquarium:
        """ Add BaseElement or Fish to contents """

        if issubclass(type(other), BaseElement):
            self._add_element(other)
        else:
            self.objects.append(other)
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

        if obj is not None:
            startx += real_length(obj.skin)
            endx -= real_length(obj.skin)

        return Position(
            randint(startx + 1, endx - 1), randint(starty + 1, endy - 1)
        )

    def notify(self, event: AquariumEvent, data: Optional[Any] = None) -> None:
        """ Notify Aquarium of events """

        if event is AquariumEvent.FOOD_DESTROYED:
            # NOTE: this should never be raised, but even then
            #       should be limited by an option
            if not isinstance(data, Food):
                raise Exception(
                    f"Object {data} is not food! How did this happen?"
                )

            self.objects.remove(data)
            for f in self.fish():
                f.notify(event, data)

        elif event is AquariumEvent.TARGET_REACHED:
            if not isinstance(data, Fish):
                raise Exception(
                    f"Object {data} is not fish! How did this happen?"
                )

            # this is not working the way it should be
            # if data in self._target_reached:
            #    return

            # self._target_reached.append(data)
            # reached_fish = len(self._target_reached)
            # total_fish = len(list(self.fish()))

            self.target_pos = None

    def pause(self, value: bool = True) -> None:
        """ Pause updates """

        self._is_paused = value

    def fish_at(self, pos: Position) -> Optional[Fish]:
        """ Return the thing that is at the position given """

        px, py = pos
        for e in self.objects:
            if not isinstance(e, Fish):
                continue

            startx, starty, endx, endy = e.bounds
            if starty <= py <= endy and startx <= px <= endx:
                return e

        return None

    def contains(self, pos: Position) -> bool:
        """ Return if position is contained within self """

        return self.bounds.contains(pos)

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

    def update(self) -> None:
        """ Update elements in self.objects"""

        def show_element(element: Union[Food, Fish]) -> None:
            """ Show element """

            element.wipe()
            element.update()
            element.show()

        if self._is_paused:
            return

        for food in self.foods():
            show_element(food)

        for fish in self.fish():
            show_element(fish)
