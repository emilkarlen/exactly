from exactly_lib.symbol.logic.program.program_sdv import ProgramStv, ProgramSdv
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_system.value_type import ValueType
from exactly_lib_test.symbol.test_resources import symbol_usage_assertions as asrt_sym_usage
from exactly_lib_test.symbol.test_resources.restrictions_assertions import is_value_type_restriction
from exactly_lib_test.symbol.test_resources.symbols_setup import SdvSymbolContext
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion

IS_PROGRAM_REFERENCE_RESTRICTION = is_value_type_restriction(ValueType.PROGRAM)


def is_program_reference_to(symbol_name: str) -> ValueAssertion:
    return asrt_sym_usage.matches_reference(asrt.equals(symbol_name),
                                            IS_PROGRAM_REFERENCE_RESTRICTION)


class ProgramSymbolContext(SdvSymbolContext[ProgramStv]):
    def __init__(self,
                 name: str,
                 sdtv: ProgramStv,
                 ):
        super().__init__(name)
        self._sdtv = sdtv

    @staticmethod
    def of_generic(name: str, sdv: ProgramSdv) -> 'ProgramSymbolContext':
        return ProgramSymbolContext(
            name,
            ProgramStv(sdv)
        )

    @property
    def sdtv(self) -> ProgramStv:
        return self._sdtv

    @property
    def reference_assertion(self) -> ValueAssertion[SymbolReference]:
        return is_program_reference_to(self.name)
