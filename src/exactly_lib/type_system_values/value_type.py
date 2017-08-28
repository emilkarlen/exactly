from enum import Enum


class ElementType(Enum):
    SYMBOL = 1
    FILE_SELECTOR = 2


class SymbolValueType(Enum):
    STRING = 0
    PATH = 1
    LIST = 2


class ValueType(Enum):
    STRING = 0
    PATH = 1
    LIST = 2
    FILE_SELECTOR = 3
