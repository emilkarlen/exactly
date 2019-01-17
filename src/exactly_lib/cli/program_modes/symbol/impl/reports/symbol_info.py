from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Iterator, Optional

from exactly_lib.definitions.test_case.instructions.define_symbol import ANY_TYPE_INFO_DICT
from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.symbol_usage import SymbolDefinition, SymbolReference
from exactly_lib.test_case.phase_identifier import Phase
from exactly_lib.type_system.value_type import ValueType

SYMBOL_INFO = TypeVar('SYMBOL_INFO')


class ContextAnd(Generic[SYMBOL_INFO]):
    def __init__(self,
                 phase: Phase,
                 source_location_info: Optional[SourceLocationInfo],
                 value: SYMBOL_INFO):
        self._phase = phase
        self._source_location_info = source_location_info
        self._value = value

    def phase(self) -> Phase:
        return self._phase

    def source_location_info(self) -> Optional[SourceLocationInfo]:
        return self._source_location_info

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
                 phase: Phase,
                 definition: SymbolDefinition,
                 references: List[ContextAnd[SymbolReference]]):
        self.phase = phase
        self.definition = definition
        self.references = references

    def name(self) -> str:
        return self.definition.name

    def value_type(self) -> ValueType:
        return self.definition.resolver_container.resolver.value_type

    def type_identifier(self) -> str:
        return ANY_TYPE_INFO_DICT[self.value_type()].identifier


class DefinitionsResolver(ABC):
    @abstractmethod
    def definitions(self) -> Iterator[SymbolDefinitionInfo]:
        pass
