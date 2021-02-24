from typing import Optional

from exactly_lib.impls.types.program.sdvs import program_symbol_sdv
from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolUsage
from exactly_lib.symbol.value_type import ValueType
from exactly_lib.type_val_deps.types.program.sdv.accumulated_components import AccumulatedComponents
from exactly_lib.type_val_deps.types.program.sdv.program import ProgramSdv
from exactly_lib_test.impls.types.program.test_resources.program_sdvs import \
    arbitrary__without_symbol_references
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.symbol_context import ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.test_resources.any_.restrictions_assertions import \
    is_reference_restrictions__value_type
from exactly_lib_test.type_val_deps.test_resources.full_deps.symbol_context import LogicSymbolValueContext, \
    LogicTypeSymbolContext
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramOfSymbolReferenceAbsStx

NON_EXISTING_SYSTEM_PROGRAM = 'a-non-existing-system-program'

IS_PROGRAM_REFERENCE_RESTRICTION = is_reference_restrictions__value_type((ValueType.PROGRAM,))


def is_reference_to_program__usage(symbol_name: str) -> Assertion[SymbolUsage]:
    return asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                            IS_PROGRAM_REFERENCE_RESTRICTION)


def is_reference_to_program(symbol_name: str) -> Assertion[SymbolReference]:
    return asrt.is_instance_with(
        SymbolReference,
        asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                         IS_PROGRAM_REFERENCE_RESTRICTION)
    )


class ProgramSymbolValueContext(LogicSymbolValueContext[ProgramSdv]):
    def __init__(self,
                 sdv: ProgramSdv,
                 definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
                 ):
        super().__init__(sdv, definition_source)

    @staticmethod
    def of_sdv(sdv: ProgramSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'ProgramSymbolValueContext':
        return ProgramSymbolValueContext(sdv,
                                         definition_source)

    @staticmethod
    def of_arbitrary_value() -> 'ProgramSymbolValueContext':
        return ARBITRARY_SYMBOL_VALUE_CONTEXT

    @property
    def value_type(self) -> ValueType:
        return ValueType.PROGRAM

    def reference_assertion(self, symbol_name: str) -> Assertion[SymbolReference]:
        return is_reference_to_program(symbol_name)


class ProgramSymbolContext(LogicTypeSymbolContext[ProgramSdv]):
    def __init__(self,
                 name: str,
                 value: ProgramSymbolValueContext,
                 ):
        super().__init__(name)
        self._value = value

    @staticmethod
    def of_sdv(name: str,
               sdv: ProgramSdv,
               definition_source: Optional[SourceLocationInfo] = ARBITRARY_LINE_SEQUENCE_FOR_DEFINITION,
               ) -> 'ProgramSymbolContext':
        return ProgramSymbolContext(
            name,
            ProgramSymbolValueContext.of_sdv(sdv, definition_source)
        )

    @staticmethod
    def of_arbitrary_value(name: str) -> 'ProgramSymbolContext':
        return ProgramSymbolContext(name, ARBITRARY_SYMBOL_VALUE_CONTEXT)

    @property
    def value(self) -> ProgramSymbolValueContext:
        return self._value

    @property
    def reference_sdv(self) -> ProgramSdv:
        return program_symbol_sdv.ProgramSdvForSymbolReference(self.name,
                                                               AccumulatedComponents.empty())

    @property
    def abstract_syntax(self) -> ProgramOfSymbolReferenceAbsStx:
        return ProgramOfSymbolReferenceAbsStx(self.name)


ARBITRARY_SYMBOL_VALUE_CONTEXT = ProgramSymbolValueContext.of_sdv(arbitrary__without_symbol_references())
