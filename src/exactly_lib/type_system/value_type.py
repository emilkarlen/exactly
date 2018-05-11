from enum import Enum


class TypeCategory(Enum):
    DATA = 1
    LOGIC = 2


class DataValueType(Enum):
    STRING = 0
    PATH = 1
    LIST = 2


class LogicValueType(Enum):
    LINE_MATCHER = 1
    FILE_MATCHER = 2
    STRING_TRANSFORMER = 3
    PROGRAM = 4


class ValueType(Enum):
    STRING = 0
    PATH = 1
    LIST = 2

    LINE_MATCHER = 3
    FILE_MATCHER = 4
    STRING_TRANSFORMER = 5
    PROGRAM = 6


VALUE_TYPE_2_TYPE_CATEGORY = {
    ValueType.STRING: TypeCategory.DATA,
    ValueType.PATH: TypeCategory.DATA,
    ValueType.LIST: TypeCategory.DATA,

    ValueType.FILE_MATCHER: TypeCategory.LOGIC,
    ValueType.LINE_MATCHER: TypeCategory.LOGIC,
    ValueType.STRING_TRANSFORMER: TypeCategory.LOGIC,
    ValueType.PROGRAM: TypeCategory.LOGIC,
}
