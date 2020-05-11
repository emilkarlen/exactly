from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Iterator, Optional

from exactly_lib.definitions.test_case.instructions.define_symbol import ANY_TYPE_INFO_DICT
from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolDefinition
from exactly_lib.test_case.phase_identifier import Phase
from exactly_lib.type_system.value_type import ValueType

SYMBOL_INFO = TypeVar('SYMBOL_INFO')


class SourceInfo:
    def __init__(self,
                 source_location_info: Optional[SourceLocationInfo],
                 source_lines: Optional[List[str]]):
        self.source_location_info = source_location_info
        self.source_lines = source_lines

    @staticmethod
    def of_location_info(location_info: SourceLocationInfo):
        return SourceInfo(location_info, None)

    @staticmethod
    def of_lines(lines: List[str]):
        return SourceInfo(None, lines)

    @staticmethod
    def empty():
        return SourceInfo(None, None)


class ContextAnd(Generic[SYMBOL_INFO]):
    def __init__(self,
                 phase: Phase,
                 source_info: SourceInfo,
                 value: SYMBOL_INFO):
        self._phase = phase
        self._source_info = source_info
        self._value = value

    def phase(self) -> Phase:
        return self._phase

    def source_info(self) -> SourceInfo:
        return self._source_info

    def value(self) -> SYMBOL_INFO:
        return self._value


class SymUsageInPhase(Generic[SYMBOL_INFO]):
    def __init__(self,
                 phase: Phase,
                 value: SYMBOL_INFO):
        self._phase = phase
        self._value = value

    def value(self) -> SYMBOL_INFO:
        return self._value

    def phase(self) -> Phase:
        return self._phase


class SymbolDefinitionInfo:
    def __init__(self,
                 phase: Optional[Phase],
                 definition: SymbolDefinition,
                 references: List[ContextAnd[SymbolReference]]):
        self.phase = phase
        self.definition = definition
        self.references = references

    @staticmethod
    def new_builtin(definition: SymbolDefinition,
                    references: List[ContextAnd[SymbolReference]]) -> 'SymbolDefinitionInfo':
        return SymbolDefinitionInfo(None, definition, references)

    def is_user_defined(self) -> bool:
        return self.phase is not None

    def name(self) -> str:
        return self.definition.name

    def value_type(self) -> ValueType:
        return self.definition.symbol_container.value_type

    def type_identifier(self) -> str:
        return ANY_TYPE_INFO_DICT[self.value_type()].identifier


class DefinitionsResolver(ABC):
    @abstractmethod
    def definitions(self) -> Iterator[SymbolDefinitionInfo]:
        pass
