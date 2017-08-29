from enum import Enum


class ElementType(Enum):
    SYMBOL = 1
    LOGIC = 2


class SymbolValueType(Enum):
    STRING = 0
    PATH = 1
    LIST = 2


class LogicValueType(Enum):
    FILE_SELECTOR = 1
    LINES_TRANSFORMER = 2


class ValueType(Enum):
    STRING = 0
    PATH = 1
    LIST = 2
    FILE_SELECTOR = 3
    LINES_TRANSFORMER = 4


VALUE_TYPE_2_ELEMENT_TYPE = {
    ValueType.STRING: ElementType.SYMBOL,
    ValueType.PATH: ElementType.SYMBOL,
    ValueType.LIST: ElementType.SYMBOL,

    ValueType.FILE_SELECTOR: ElementType.LOGIC,
    ValueType.LINES_TRANSFORMER: ElementType.LOGIC,
}
