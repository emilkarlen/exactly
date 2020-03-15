from exactly_lib.symbol.logic.program.program_sdv import ProgramStv, ProgramSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_system.value_type import ValueType
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.symbols_setup import LogicTypeSymbolContext, LogicSymbolTypeContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

IS_PROGRAM_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.PROGRAM)


def is_program_reference_to(symbol_name: str) -> ValueAssertion:
    return asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                            IS_PROGRAM_REFERENCE_RESTRICTION)


class ProgramSymbolTypeContext(LogicSymbolTypeContext[ProgramStv]):
    @staticmethod
    def of_generic(sdv: ProgramSdv) -> 'ProgramSymbolTypeContext':
        return ProgramSymbolTypeContext(ProgramStv(sdv))

    def reference_assertion(self, symbol_name: str) -> ValueAssertion[SymbolReference]:
        return is_program_reference_to(symbol_name)


class ProgramSymbolContext(LogicTypeSymbolContext[ProgramStv]):
    def __init__(self,
                 name: str,
                 type_context: ProgramSymbolTypeContext,
                 ):
        super().__init__(name, type_context)

    @staticmethod
    def of_sdtv(name: str, sdtv: ProgramStv) -> 'ProgramSymbolContext':
        return ProgramSymbolContext(
            name,
            ProgramSymbolTypeContext(sdtv)
        )

    @staticmethod
    def of_generic(name: str, sdv: ProgramSdv) -> 'ProgramSymbolContext':
        return ProgramSymbolContext(
            name,
            ProgramSymbolTypeContext.of_generic(sdv)
        )
