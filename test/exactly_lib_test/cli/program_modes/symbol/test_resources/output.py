import functools
from typing import List

from exactly_lib.definitions.entity import types
from exactly_lib.definitions.test_case.instructions.define_symbol import ANY_TYPE_INFO_DICT
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.string import lines_content

_NO_REFS_INFO = '(unused)'


class SymbolReport:
    def __init__(self,
                 name: str,
                 value_type: ValueType,
                 num_refs: int):
        self._name = name
        self._value_type = value_type
        self._num_refs = num_refs
        self._type_identifier = ANY_TYPE_INFO_DICT[value_type].identifier
        self._num_refs_string = '(' + str(self._num_refs) + ')'

    def name(self) -> str:
        return self._name

    def type_identifier(self) -> str:
        return self._type_identifier

    def num_refs(self) -> int:
        return self._num_refs

    def name_length(self) -> int:
        return len(self._name)

    def type_identifier_length(self) -> int:
        return len(self._type_identifier)

    def num_refs_string(self) -> str:
        return self._num_refs_string

    def num_refs_string_length(self) -> int:
        return len(self._num_refs_string)


def def_of_string(symbol_name: str) -> str:
    return types.STRING_TYPE_INFO.identifier + ' ' + symbol_name


def list_of(symbols: List[SymbolReport]) -> str:
    max_type_ident_len = functools.reduce(int_max,
                                          map(SymbolReport.type_identifier_length,
                                              symbols),
                                          0)
    max_num_refs_len = functools.reduce(int_max,
                                        map(SymbolReport.num_refs_string_length,
                                            symbols),
                                        0)
    formatting_str = '{type: <{type_width}} {num_refs_info: <{num_refs_width}} {name}'

    def format_symbol(symbol: SymbolReport) -> str:
        s = formatting_str.format(type=symbol.type_identifier(),
                                  type_width=max_type_ident_len,
                                  name=symbol.name(),
                                  num_refs_width=max_num_refs_len,
                                  num_refs_info=symbol.num_refs_string())
        return s.strip()

    return lines_content([
        format_symbol(symbol)
        for symbol in symbols
    ])


def int_max(x: int, y: int) -> int:
    return max(x, y)
