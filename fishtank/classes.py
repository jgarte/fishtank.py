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
    FishEvent,
    BoundaryError,
    FishType,
    FishProperties,
)


class Position:
    """Class for easier & more legible positions"""

    # having variables named x and y makes most sense
    # pylint: disable=invalid-name
    def __init__(self, x: int = 0, y: int = 0, xy: Optional[list[int]] = None):
        if xy:
            self.x, self.y = xy
        else:
            self.x = x
            self.y = y

    def __eq__(self, other: object) -> bool:
        """Return if two Position objects are equal"""

        if not isinstance(other, Position):
            raise NotImplementedError()

        return self.x == other.x and self.y == other.y

    def __gt__(self, other: object) -> bool:
        """Return if self.x > other.x"""

        if not isinstance(other, Position):
            raise NotImplementedError()

        return self.x > other.x

    def __add__(self, other: object) -> Position:
        """Return new Position containing added values"""

        if not isinstance(other, Position):
            raise NotImplementedError(f"Cannot add {type(other)} object to Position!")

        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: object) -> Position:
        """Return new Position containing substracted values"""

        if not isinstance(other, Position):
            raise NotImplementedError()

        return Position(self.x - other.x, self.y - other.y)

    def __repr__(self) -> str:
        """Return string of self"""

        return f"Position({self.x},{self.y})"

    def __iter__(self) -> Generator[int, None, None]:
        """Yield values of self.x, self.y; allows: x, y = Position()"""

        for v in self.x, self.y:
            yield v

    def __bool__(self) -> bool:
        return True

    def show(self) -> None:
        """Print self"""

        print(f"\033[{self.y};{self.x}Hx")

    def wipe(self) -> None:
        """Wipe character at self.x & self.y"""

        print(f"\033[{self.y};{self.x}H ")

    def distance_to(self, other: object) -> float:
        """Return distance from self to other"""

        if not isinstance(other, Position):
            raise NotImplementedError()

        return sqrt((other.x - self.x) ** 2 + (other.y - self.y) ** 2)


class Boundary:
    """Boundary made up by two Position objects, non-inclusive of borders"""

    def __init__(self, pos1: Position, pos2: Position) -> None:
        """Initialize object"""

        self.start = pos1
        self.end = pos2

    def __iter__(self) -> Generator[int, None, None]:
        """Iterate start and end positions"""

        for pos in [self.start, self.end]:
            for coord in pos:
                yield coord

    def _contains_coordinates(self, other: Position) -> bool:
        """Helper to get if self contains other"""

        error = self.error(other)

        if error is None:
            return True

        return False

    def positions(self) -> Generator[Position, None, None]:
        """Iterate positions"""

        for pos in self.start, self.end:
            yield pos

    def error(self, other: Position) -> Optional[BoundaryError]:
        """Get BoundaryError from other in self"""

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
        """Return whether self contains other"""

        if isinstance(other, Position):
            return self._contains_coordinates(other)

        pos1, pos2 = other.start, other.end
        return self._contains_coordinates(pos1) and self._contains_coordinates(pos2)

    def show(self) -> None:
        """Print coordinates"""

        self.start.show()
        self.end.show()

    def update(
        self, start: Optional[Position] = None, end: Optional[Position] = None
    ) -> None:
        """Update coordinates"""

        if start is not None:
            assert isinstance(start, Position)

            self.start = start

        if end is not None:
            assert isinstance(end, Position)

            self.end = end

    def __repr__(self) -> str:
        """Stringify object"""

        return f"Boundary({self.start.x}, {self.start.y}, {self.end.x}, {self.end.y})"


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

    """

    # it makes sense for this class to have as many attributes as it does.
    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent: Aquarium, properties: FishProperties):
        """Set up instance"""

        self.path: list[tuple[Position, int]] = []
        self.pigment: list[int] = []
        self.forced_pigment: Optional[list[int]] = None
        self.skin_length: int = 0
        self.stages: list[str]
        self.bounds: Optional[Boundary] = None
        self.skin: str = ""
        self.variant: str
        self.species: str
        self.age: int

        self._pos: Optional[Position] = None
        self._skins: tuple[str, str]
        self._follow_target: Optional[Union[Fish, Food]] = None
        self._food: Optional[Food] = None
        self._heading: int = 0

        self.parent = parent
        self._set_properties(properties)
        self.pigment = self.get_pigment()

        self.heading_left = -1
        self.heading_right = 1

        # trigger event to set skins
        self.notify(FishEvent.AGE_CHANGED, self)
        self.update()

    def _set_properties(self, properties: FishProperties) -> None:
        for key, value in properties.items():
            if key == "pos":
                # this is a no-case, but mypy complains
                if not isinstance(value, list):
                    raise NotImplementedError()

                if not all(isinstance(v, int) for v in value):
                    raise NotImplementedError()

                posx, posy = value
                value = Position(posx, posy)

            setattr(self, key, value)

    @staticmethod
    def _reverse_skin(skin: str) -> str:
        """Return char by char reversed version of skin"""

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
    def pos(self) -> Optional[Position]:
        """Return position"""

        return self._pos

    @pos.setter
    def pos(self, value: Position) -> None:
        """Set new position and update bounds"""

        self._pos = value
        start, end = self._get_bounds()

        if self.bounds is not None:
            self.bounds.update(start, end)

        else:
            self.bounds = Boundary(start, end)

    def _get_bounds(self, pos: Optional[Position] = None) -> tuple[Position, Position]:
        """Return boundaries of object"""

        if self.pos is None:
            raise TypeError("self.pos cannot be None during _get_bounds.")

        if pos is None:
            pos = self.pos

        posx, posy = pos
        start = Position(posx, posy)
        end = Position(posx + real_length(self.skin), posy)

        return start, end

    def __repr__(self) -> Any:
        """__repr__ method that handles pigmenting

        Note:
            pytermgui.gradient() and this function
            should return str, and will do so once
            I get around to the rewrite.
        """

        # skins are right-headed
        if self._heading is self.heading_left:
            skin = self._skins[1]
            pigment = list(reversed(self.pigment))

        else:
            skin = self._skins[0]
            pigment = self.pigment

        return gradient(skin, pigment)

    def _position_valid(self, pos: Position) -> bool:
        """Return validity (is within self.parent.bounds) of pos
        This currently doesn't do anything, and it might not be
        needed in the future."""

        if self.parent is None:
            return False

        posx, posy = pos
        start_pos = Position(posx, posy)
        end_pos = Position(posx + real_length(self.skin), posy)

        start_error = self.parent.bounds.error(start_pos)
        end_error = self.parent.bounds.error(end_pos)
        valid_errors = [BoundaryError.Y, BoundaryError.XY, None]

        if start_error in valid_errors and end_error in valid_errors:
            return True

        return False

    def get_pigment(self) -> list[int]:
        """Get pigmentation using self.variant"""

        if self.forced_pigment is not None:
            return self.forced_pigment

        if (available := self.pigment) is not None:
            if available == []:
                return []

            pigment = []
            length = max(len(clean_ansi(l)) for l in self.stages)

            for _ in range(length):
                if len(available) > 1:
                    index = randint(0, len(available) - 1)
                else:
                    index = 0

                pigment.append(available[index])

            return pigment

        return self.pigment

    def get_path(self, pos: Position) -> list[tuple[Position, int]]:
        """Get position to pos, return it as a list of Position-s"""

        if self.pos is None:
            raise TypeError("self.pos cannot be None while getting path.")

        startx, starty = self.pos
        endx, endy = pos

        # x dif, x direction
        diffx = abs(endx - startx)
        intbuff_x = 1 if startx < endx else -1

        # y dif, y direction
        diffy = -abs(endy - starty)
        intbuff_y = 1 if starty < endy else -1

        if intbuff_x == 1:
            heading = self.heading_right
        else:
            heading = self.heading_left

        # error
        error = diffx + diffy

        path = []
        while True:
            pos = Position(startx, starty)
            if not self._position_valid(pos):
                break

            path.append((pos, heading))
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

    def get_new_path(self) -> list[tuple[Position, int]]:
        """Get new target according to self.type
        Note: this should handle different FishTypes
        """

        return self.get_path(self.parent.get_next_position(self))

    def distance_to(self, other: Union[Food, Fish]) -> float:
        """Return distance between two objects"""

        if type(other) not in [Food, Fish]:
            raise NotImplementedError(f"Why are we getting distance to {type(other)}?")

        if self.pos is None:
            raise TypeError("self.pos cannot be None during distance_to")

        if self.pos > other.pos:
            offset = 2
        else:
            offset = self.skin_length - 1

        return self.pos.distance_to(other.pos) - offset

    def consume_food(self) -> bool:
        """Try to consume food"""

        if self._follow_target is None:
            return False

        if not isinstance(self._follow_target, Food):
            return False

        if self.pos is None:
            raise TypeError("self.pos cannot be None during consume_food")

        food = self._follow_target

        if food.pos is None:
            raise TypeError("food.pos cannot be None during consume_food")

        if self._heading is self.heading_right:
            target_distance = self.skin_length - 1
        else:
            target_distance = 2

        distance = self.distance_to(food)

        if distance <= target_distance and self.pos.y == food.pos.y:
            food.health -= 1

            if randint(0, 10) == 1 and self.age < len(self.stages) - 1:
                self.age += 1
                self.notify(FishEvent.AGE_CHANGED, self)

            return True

        return False

    def update(self) -> Optional[Position]:
        """Do next position update"""

        if self._follow_target is not None:
            if self._follow_target.pos is None:
                raise TypeError("self._follow_target.pos cannot be None during update")

            self.path = self.get_path(self._follow_target.pos)

        if self.consume_food():
            return self.pos

        if len(self.path) > 1:
            # There is an extra element at the start of path if following,
            # as the path gets regenerated every update. If we don't do an
            # extra pop, the fish will stay in place.
            if self._follow_target is not None:
                self.path.pop(0)

            self.pos, self._heading = self.path.pop(0)

        else:
            self.parent.notify(AquariumEvent.TARGET_REACHED, self)

            candidates = []
            for food in self.parent.foods():
                candidates.append((food, self.distance_to(food)))

            if len(candidates) > 0:
                candidates.sort(key=lambda value: value[1])
                food, _ = candidates[0]
                self._follow_target = food

            else:
                path = []
                if self.pos is not None:
                    heading = self._heading

                    for i in range(randint(3, 10)):
                        if i >= 4 and i % 3 == 0:
                            heading = heading * -1

                        path += [(self.pos, heading)]

                self.path = path + self.get_new_path()

        return self.pos

    def notify(self, event: Event, data: Optional[Any]) -> None:
        """Notify fish of some event"""

        if event == AquariumEvent.FOOD_DESTROYED:
            if data is not self._follow_target:
                return

            self._follow_target = None
            if randint(1, 3) > 1:
                self.path = []
                self.update()

        elif event == AquariumEvent.FOOD_AVAILABLE:
            if not isinstance(data, Food):
                raise Exception(f"Object {data} is not Food! How did this happen?")

            if self.distance_to(data) < 20:
                self._follow_target = data

        elif event == FishEvent.AGE_CHANGED:
            _skin = self.stages[self.age]
            self._skins = _skin, self._reverse_skin(_skin)
            self.skin = self._skins[0]

    def wipe(self) -> None:
        """Wipe fish's skin at its current position"""

        if self.pos is None:
            return

        posx, posy = self.pos
        print(f"\033[{posy};{posx}H" + real_length(self.skin) * " ")

    def show(self) -> None:
        """Show repr(self) at self.pos"""

        if self.pos is None:
            return

        posx, posy = self.pos
        print(f"\033[{posy};{posx}H" + repr(self))


class Food:
    """fud"""

    # it makes sense for this class to have this many attributes.
    # pylint: disable=too-many-instance-attributes
    def __init__(
        self, parent: Aquarium, health: int = 5, pos: Optional[Position] = None
    ):
        """Initialize object"""

        self.bounds = Boundary(Position(0, 0), Position(0, 0))
        self.health: int = health
        self.skin: str = "#"
        self.path: list[Position] = []
        self.counter: int = 0
        self._is_stopped: bool = False
        self._idle_framecount: int = 0

        if pos is None:
            self._pos = Position()
        else:
            self._pos = pos

        self.parent = parent

    @property
    def pos(self) -> Optional[Position]:
        """Get self._pos"""

        return self._pos

    @pos.setter
    def pos(self, value: Position) -> None:
        """Set self._pos"""

        self._pos = value

        if self.pos is not None:
            self.bounds.update(self.pos, self.pos + Position(x=real_length(self.skin)))

    def stop(self) -> None:
        """Stop updates of object"""

        self._is_stopped = True

    def destroy(self) -> None:
        """Remove self from parent"""

        self.parent.notify(AquariumEvent.FOOD_DESTROYED, self)
        self.wipe()

    def update(self) -> None:
        """Update position & path"""

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

        if self.pos is None:
            raise TypeError("self.pos cannot be None during update.")

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
        """Clear char at pos"""

        if self.pos is None:
            return

        posx, posy = self.pos
        print(f"\033[{posy};{posx}H" + real_length(self.skin) * " ")

    def show(self) -> None:
        """Print self to pos"""

        if self.pos is None:
            return

        posx, posy = self.pos
        print(f"\033[{posy};{posx}H" + self.skin)


# as long as pytermgui is not typed this error would occur.
class Aquarium(Container):  # type: ignore[misc]
    """An object to store & update fish"""

    # pylint: disable=invalid-name
    def __init__(
        self,
        pos: Optional[list[int]] = None,
        _width: int = 70,
        _height: int = 25,
    ):
        """Set up object"""

        super().__init__(width=_width, height=_height)

        self.fps: int
        self.objects: list[Union[Fish, Food]] = []
        self.target_pos: Union[Position, None] = None
        self.bounds: Boundary

        self._is_paused: bool = False
        self._prev_target_pos: Optional[Position] = None

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
        self.bounds = self._get_bounds()

    def __iter__(self) -> Generator[Union[Fish, Food], None, None]:
        """Iterate through fish children"""

        for obj in self.objects:
            yield obj

    def __add__(self, other: Union[BaseElement, Fish]) -> Aquarium:
        """Add BaseElement or Fish to contents"""

        if issubclass(type(other), BaseElement):
            self._add_element(other)
        else:
            self.objects.append(other)

            while not self.contains(other):
                other.pos = self._get_position_in_bounds(other)
            other.path = []

            other.parent = self

            if isinstance(other, Food):
                for fish in self.fish():
                    fish.notify(AquariumEvent.FOOD_AVAILABLE, other)
            self.pause(False)

        return self

    def __iadd__(self, other: Union[BaseElement, Fish]) -> Aquarium:
        """Execute __add__, return self"""

        return self.__add__(other)

    def _get_bounds(self) -> Boundary:
        """Return boundaries of object"""

        x, y = self.pos
        start = Position(x + 1, y + 1)
        end = Position(x + self.width - 1, y + self.height)

        return Boundary(start, end)

    def _get_position_in_bounds(self, obj: Optional[Fish] = None) -> Position:
        """Return a Position() object that is guaranteed to be within bounds"""

        startx, starty, endx, endy = self.bounds

        if obj is not None:
            startx += real_length(obj.skin) - 1
            endx -= real_length(obj.skin) + 1

        return Position(randint(startx + 1, endx - 1), randint(starty + 1, endy - 1))

    def foods(self) -> Generator[Food, None, None]:
        """Iterate through foods"""

        for obj in self.objects:
            if isinstance(obj, Food):
                yield obj

    def fish(self) -> Generator[Fish, None, None]:
        """Iterate through fish"""

        for obj in self.objects:
            if isinstance(obj, Fish):
                yield obj

    def notify(self, event: AquariumEvent, data: Optional[Any] = None) -> None:
        """Notify Aquarium of events"""

        if event is AquariumEvent.FOOD_DESTROYED:
            # NOTE: this should never be raised, but even then
            #       should be limited by an option
            if not isinstance(data, Food):
                raise Exception(f"Object {data} is not food! How did this happen?")

            if data in self.objects:
                self.objects.remove(data)

            for f in self.fish():
                f.notify(event, data)

        elif event is AquariumEvent.TARGET_REACHED:
            if not isinstance(data, Fish):
                raise Exception(f"Object {data} is not fish! How did this happen?")

            self._prev_target_pos = self.target_pos
            self.target_pos = None

    def pause(self, value: bool = True) -> None:
        """Pause updates"""

        self._is_paused = value

    def fish_at(self, pos: Position) -> Optional[Fish]:
        """Return the thing that is at the position given"""

        px, py = pos
        for e in self.objects:
            if not isinstance(e, Fish):
                continue

            if e.bounds is None:
                continue

            startx, starty, endx, endy = e.bounds
            if starty <= py <= endy and startx <= px <= endx:
                return e

        return None

    def contains(self, obj: Fish) -> bool:
        """Return if obj is contained within self"""

        if obj.bounds is None or self.bounds is None:
            return False

        return self.bounds.contains(obj.bounds)

    def move(self, pos: list[int], _wipe: bool = False) -> Aquarium:
        """Implement move method using Position-s"""

        self.pos = Position(xy=pos)
        if _wipe:
            self.wipe()
        self.get_border()

        return self

    def get_next_position(self, obj: Optional[Fish] = None) -> Position:
        """Return a target position for fish"""

        if self.target_pos is None:
            minx, miny, maxx, maxy = self.bounds
            if obj is not None:
                maxx -= obj.skin_length + 1

            newx = randint(minx + 1, maxx - 1)
            newy = randint(miny + 1, maxy - 1)
            self.target_pos = Position(newx, newy)

        return self.target_pos

    def update(self) -> None:
        """Update elements in self.objects"""

        def show_element(element: Union[Food, Fish]) -> None:
            """Show element"""

            element.wipe()
            element.update()
            element.show()

        if self._is_paused:
            return

        for food in self.foods():
            show_element(food)

        for fish in self.fish():
            show_element(fish)
