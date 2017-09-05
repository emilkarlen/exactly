from enum import Enum


class ElementType(Enum):
    SYMBOL = 1
    LOGIC = 2


class SymbolValueType(Enum):
    STRING = 0
    PATH = 1
    LIST = 2


class LogicValueType(Enum):
    LINE_MATCHER = 1
    FILE_MATCHER = 2
    LINES_TRANSFORMER = 3


class ValueType(Enum):
    STRING = 0
    PATH = 1
    LIST = 2

    LINE_MATCHER = 3
    FILE_MATCHER = 4
    LINES_TRANSFORMER = 5


VALUE_TYPE_2_ELEMENT_TYPE = {
    ValueType.STRING: ElementType.SYMBOL,
    ValueType.PATH: ElementType.SYMBOL,
    ValueType.LIST: ElementType.SYMBOL,

    ValueType.FILE_MATCHER: ElementType.LOGIC,
    ValueType.LINE_MATCHER: ElementType.LOGIC,
    ValueType.LINES_TRANSFORMER: ElementType.LOGIC,
}
