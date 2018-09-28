import enum
from enum import Enum


@enum.unique
class TypeCategory(Enum):
    DATA = 1
    LOGIC = 2


@enum.unique
class DataValueType(Enum):
    STRING = 0
    PATH = 1
    LIST = 2


@enum.unique
class LogicValueType(Enum):
    LINE_MATCHER = 1
    FILE_MATCHER = 2
    STRING_MATCHER = 3
    STRING_TRANSFORMER = 4
    PROGRAM = 5


@enum.unique
class ValueType(Enum):
    STRING = 0
    PATH = 1
    LIST = 2

    LINE_MATCHER = 3
    FILE_MATCHER = 4
    STRING_MATCHER = 5
    STRING_TRANSFORMER = 6
    PROGRAM = 7


VALUE_TYPE_2_TYPE_CATEGORY = {
    ValueType.STRING: TypeCategory.DATA,
    ValueType.PATH: TypeCategory.DATA,
    ValueType.LIST: TypeCategory.DATA,

    ValueType.FILE_MATCHER: TypeCategory.LOGIC,
    ValueType.LINE_MATCHER: TypeCategory.LOGIC,
    ValueType.STRING_MATCHER: TypeCategory.LOGIC,
    ValueType.STRING_TRANSFORMER: TypeCategory.LOGIC,
    ValueType.PROGRAM: TypeCategory.LOGIC,
}

TYPE_CATEGORY_2_VALUE_TYPE_SEQUENCE = {
    TypeCategory.DATA: [
        vt
        for vt in VALUE_TYPE_2_TYPE_CATEGORY.keys()
        if VALUE_TYPE_2_TYPE_CATEGORY[vt] is TypeCategory.DATA
    ],
    TypeCategory.LOGIC: [
        vt
        for vt in VALUE_TYPE_2_TYPE_CATEGORY.keys()
        if VALUE_TYPE_2_TYPE_CATEGORY[vt] is TypeCategory.LOGIC
    ],
}
