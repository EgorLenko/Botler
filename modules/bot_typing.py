from dataclasses import dataclass
from typing import NewType

from aiogram import types


@dataclass
class DCBaseLocation:
    latitude: float
    longitude: float


@dataclass
class TGLocation(DCBaseLocation):
    location_msg: types.Message


Unpackable_1D = list | tuple | set

PositiveInt = NewType('PositiveInt', int)
