import functools
from typing import List

from exactly_lib.definitions.entity import types
from exactly_lib.definitions.test_case.instructions.define_symbol import ANY_TYPE_INFO_DICT
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.string import lines_content


class SymbolReport:
    def __init__(self,
                 name: str,
                 value_type: ValueType):
        self._name = name
        self._value_type = value_type
        self._type_identifier = ANY_TYPE_INFO_DICT[value_type].identifier

    def name(self) -> str:
        return self._name

    def name_length(self) -> int:
        return len(self._name)

    def type_identifier(self) -> str:
        return self._type_identifier

    def type_identifier_length(self) -> int:
        return len(self._type_identifier)


def def_of_string(symbol_name: str) -> str:
    return types.STRING_TYPE_INFO.identifier + ' ' + symbol_name


def list_of(symbols: List[SymbolReport]) -> str:
    max_type_ident_len = functools.reduce(int_max,
                                          map(SymbolReport.type_identifier_length,
                                              symbols),
                                          0)
    max_name_len = functools.reduce(int_max,
                                    map(SymbolReport.name_length,
                                        symbols),
                                    0)
    formatting_str = '{type: <{type_width}} {name: <{name_width}}'

    def format_symbol(symbol: SymbolReport) -> str:
        s = formatting_str.format(type=symbol.type_identifier(),
                                  type_width=max_type_ident_len,
                                  name=symbol.name(),
                                  name_width=max_name_len)
        return s.strip()

    return lines_content([
        format_symbol(symbol)
        for symbol in symbols
    ])


def int_max(x: int, y: int) -> int:
    return max(x, y)
