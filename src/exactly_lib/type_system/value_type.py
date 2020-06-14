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
    FILES_MATCHER = 3
    STRING_MATCHER = 4
    STRING_TRANSFORMER = 5
    PROGRAM = 6
    FILES_CONDITION = 7


@enum.unique
class ValueType(Enum):
    STRING = 0
    PATH = 1
    LIST = 2

    LINE_MATCHER = 3
    FILE_MATCHER = 4
    FILES_MATCHER = 5
    STRING_MATCHER = 6
    STRING_TRANSFORMER = 7
    PROGRAM = 8
    FILES_CONDITION = 9


VALUE_TYPE_2_TYPE_CATEGORY = {
    ValueType.STRING: TypeCategory.DATA,
    ValueType.PATH: TypeCategory.DATA,
    ValueType.LIST: TypeCategory.DATA,

    ValueType.FILE_MATCHER: TypeCategory.LOGIC,
    ValueType.FILES_MATCHER: TypeCategory.LOGIC,
    ValueType.LINE_MATCHER: TypeCategory.LOGIC,
    ValueType.STRING_MATCHER: TypeCategory.LOGIC,
    ValueType.STRING_TRANSFORMER: TypeCategory.LOGIC,
    ValueType.PROGRAM: TypeCategory.LOGIC,
    ValueType.FILES_CONDITION: TypeCategory.LOGIC,
}

DATA_TYPE_2_VALUE_TYPE = {
    DataValueType.STRING: ValueType.STRING,
    DataValueType.PATH: ValueType.PATH,
    DataValueType.LIST: ValueType.LIST,
}

VALUE_TYPE_2_DATA_TYPE = {
    item[1]: item[0]
    for item in DATA_TYPE_2_VALUE_TYPE.items()
}

LOGIC_TYPE_2_VALUE_TYPE = {
    LogicValueType.LINE_MATCHER: ValueType.LINE_MATCHER,
    LogicValueType.FILE_MATCHER: ValueType.FILE_MATCHER,
    LogicValueType.FILES_MATCHER: ValueType.FILES_MATCHER,
    LogicValueType.STRING_MATCHER: ValueType.STRING_MATCHER,
    LogicValueType.STRING_TRANSFORMER: ValueType.STRING_TRANSFORMER,
    LogicValueType.PROGRAM: ValueType.PROGRAM,
    LogicValueType.FILES_CONDITION: ValueType.FILES_CONDITION,
}

VALUE_TYPE_2_LOGIC_TYPE = {
    item[1]: item[0]
    for item in LOGIC_TYPE_2_VALUE_TYPE.items()
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
