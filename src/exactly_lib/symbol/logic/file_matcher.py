from typing import List

from exactly_lib.symbol.logic.logic_value_resolver import LogicValueResolver
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.file_matcher import FileMatcherValue
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util.symbol_table import SymbolTable


class FileMatcherResolver(LogicValueResolver):
    """ Base class for resolvers of :class:`FileMatcher`. """

    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.FILE_MATCHER

    @property
    def value_type(self) -> ValueType:
        return ValueType.FILE_MATCHER

    @property
    def references(self) -> List[SymbolReference]:
        raise NotImplementedError('abstract method')

    def resolve(self, symbols: SymbolTable) -> FileMatcherValue:
        raise NotImplementedError('abstract method')
