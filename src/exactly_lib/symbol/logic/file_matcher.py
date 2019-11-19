from typing import List

from exactly_lib.symbol.logic.logic_type_sdv import LogicTypeSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.type_system.logic.file_matcher import FileMatcherDdv
from exactly_lib.type_system.value_type import LogicValueType, ValueType
from exactly_lib.util.symbol_table import SymbolTable


class FileMatcherSdv(LogicTypeSdv):
    """ Base class for SDVs of :class:`FileMatcher`. """

    @property
    def logic_value_type(self) -> LogicValueType:
        return LogicValueType.FILE_MATCHER

    @property
    def value_type(self) -> ValueType:
        return ValueType.FILE_MATCHER

    @property
    def references(self) -> List[SymbolReference]:
        raise NotImplementedError('abstract method')

    def resolve(self, symbols: SymbolTable) -> FileMatcherDdv:
        raise NotImplementedError('abstract method')
