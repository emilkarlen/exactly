from typing import Optional

from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.logic.program.program_sdv import ProgramStv, ProgramSdv
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolContainer
from exactly_lib.type_system.value_type import ValueType
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.symbols_setup import LogicTypeSymbolContext, LogicSymbolValueContext, \
    ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_case_utils.program.test_resources.program_sdvs import \
    arbitrary_sdv__without_symbol_references
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

IS_PROGRAM_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.PROGRAM)


def is_program_reference_to(symbol_name: str) -> ValueAssertion:
    return asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                            IS_PROGRAM_REFERENCE_RESTRICTION)


class ProgramSymbolValueContext(LogicSymbolValueContext[ProgramStv]):
    def __init__(self,
                 sdv: ProgramStv,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)

    @staticmethod
    def of_generic(sdv: ProgramSdv,
                   definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                   ) -> 'ProgramSymbolValueContext':
        return ProgramSymbolValueContext(ProgramStv(sdv),
                                         definition_source)

    @staticmethod
    def of_arbitrary_value() -> 'ProgramSymbolValueContext':
        return ARBITRARY_SYMBOL_VALUE_CONTEXT

    @property
    def value_type(self) -> ValueType:
        return ValueType.PROGRAM

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return is_program_reference_to(symbol_name)

    @property
    def container(self) -> SymbolContainer:
        return SymbolContainer(self.sdtv, self.value_type, self.definition_source)


class ProgramSymbolContext(LogicTypeSymbolContext[ProgramStv]):
    def __init__(self,
                 name: str,
                 value: ProgramSymbolValueContext,
                 ):
        super().__init__(name, value)

    @staticmethod
    def of_sdtv(name: str,
                sdtv: ProgramStv,
                definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                ) -> 'ProgramSymbolContext':
        return ProgramSymbolContext(
            name,
            ProgramSymbolValueContext(sdtv, definition_source)
        )

    @staticmethod
    def of_generic(name: str,
                   sdv: ProgramSdv,
                   definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                   ) -> 'ProgramSymbolContext':
        return ProgramSymbolContext(
            name,
            ProgramSymbolValueContext.of_generic(sdv, definition_source)
        )

    @staticmethod
    def of_arbitrary_value(name: str) -> 'ProgramSymbolContext':
        return ProgramSymbolContext(name, ARBITRARY_SYMBOL_VALUE_CONTEXT)


ARBITRARY_SYMBOL_VALUE_CONTEXT = ProgramSymbolValueContext.of_generic(arbitrary_sdv__without_symbol_references())
