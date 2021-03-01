import collections
import enum
from enum import Enum
from types import MappingProxyType
from typing import Iterable, Tuple


@enum.unique
class ValueType(Enum):
    STRING = 0
    PATH = 1
    LIST = 2

    LINE_MATCHER = 3
    FILE_MATCHER = 4
    FILES_MATCHER = 5
    STRING_MATCHER = 6
    INTEGER_MATCHER = 7
    STRING_TRANSFORMER = 8
    PROGRAM = 9
    FILES_CONDITION = 10
    STRING_SOURCE = 11


@enum.unique
class WithStrRenderingType(Enum):
    STRING = 0
    PATH = 1
    LIST = 2


W_STR_RENDERING_TYPE_2_VALUE_TYPE = MappingProxyType(
    collections.OrderedDict([
        (WithStrRenderingType.STRING, ValueType.STRING),
        (WithStrRenderingType.PATH, ValueType.PATH),
        (WithStrRenderingType.LIST, ValueType.LIST),
    ]))

VALUE_TYPE_2_W_STR_RENDERING_TYPE = MappingProxyType(
    collections.OrderedDict([
        (item[1], item[0])
        for item in W_STR_RENDERING_TYPE_2_VALUE_TYPE.items()
    ]
    ))


def sorted_types(values: Iterable[ValueType]) -> Tuple[ValueType, ...]:
    return tuple(
        sorted(values,
               key=_value_type_sorting_key)
    )


def _value_type_sorting_key(x: ValueType) -> int:
    return x.value


VALUE_TYPES_W_STR_RENDERING = sorted_types(VALUE_TYPE_2_W_STR_RENDERING_TYPE.keys())
