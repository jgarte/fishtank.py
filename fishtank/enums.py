"""
fishtank.enums
--------------
author: bczsalba


Enum classes for the program.
"""

from enum import Enum, auto


class Event(Enum):
    """ Enum class that *Event derive from. """


class AquariumEvent(Event):
    """ Enum for Aquarium().notify() calls """

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


class BoundaryError(Enum):
    """
    Enum currently limited to Aquarium.bound_error()
    TODO:
        - Bounds should be their own class, not an Aquarium function.
    """

    X = auto()
    Y = auto()
    XY = auto()
