"""
fishtank.enums
--------------
author: bczsalba


Enum classes (and types) for the program.
"""

from enum import Enum, auto
from typing import TypedDict

PositionRange = tuple[int, int]


class Event(Enum):
    """ Enum class that *Event derive from. """


class AquariumEvent(Event):
    """ Enum for Aquarium().notify() calls """

    FOOD_AVAILABLE = auto()
    FOOD_DESTROYED = auto()
    TARGET_REACHED = auto()


class FishEvent(Event):
    """
    Enum for Fish().notify() calls, currently empty

    Note:
        it could be neat to have a FOOD_ADDED element here,
        which would be used through notify() to find path to
        new food.
    """


class FishType(Enum):
    """ Types for fish """

    BOTTOM_DWELLER = auto()
    MID_WATER = auto()
    TOP_DWELLER = auto()


class BoundaryError(Enum):
    """
    Enum currently limited to Aquarium.bound_error()
    TODO:
        - Bounds should be their own class, not an Aquarium function.
    """

    X = auto()
    Y = auto()
    XY = auto()


class FishProperties(TypedDict):
    """
    Fish property dictionary

    note: pos should be of type Position,
    but that causes circular imports. we
    should figure that out.
    """

    pos: list[int]
    stages: list[str]
    type: FishType
    species: str
    variant: str
    name: str
    age: int
