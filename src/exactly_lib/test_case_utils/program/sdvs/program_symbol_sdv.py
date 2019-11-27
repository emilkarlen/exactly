from typing import Sequence

from exactly_lib.symbol import lookups
from exactly_lib.symbol.logic.program.arguments_sdv import ArgumentsSdv
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.logic.program.stdin_data_sdv import StdinDataSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironment
from exactly_lib.symbol.restriction import ValueTypeRestriction
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation import sdv_validation
from exactly_lib.test_case.validation.sdv_validation import SdvValidator, \
    SdvValidatorOfReferredSdvBase
from exactly_lib.test_case_utils.program.command import arguments_sdvs
from exactly_lib.test_case_utils.program.sdvs import accumulator
from exactly_lib.test_case_utils.program.sdvs.accumulator import ProgramElementsSdvAccumulator
from exactly_lib.type_system.logic.program.program import ProgramDdv
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import SymbolTable


class ProgramSdvForSymbolReference(ProgramSdv):
    def __init__(self,
                 symbol_name: str,
                 accumulated_elements: ProgramElementsSdvAccumulator):
        self._symbol_name = symbol_name
        self._accumulated_elements = accumulated_elements

        self._symbol_reference = SymbolReference(symbol_name,
                                                 ValueTypeRestriction(ValueType.PROGRAM))

    def new_accumulated(self,
                        additional_stdin: StdinDataSdv,
                        additional_arguments: ArgumentsSdv,
                        additional_transformations: Sequence[StringTransformerSdv],
                        additional_validation: Sequence[SdvValidator],
                        ):
        return ProgramSdvForSymbolReference(
            self._symbol_name,
            self._accumulated_elements.new_accumulated(additional_stdin,
                                                       additional_arguments,
                                                       additional_transformations,
                                                       additional_validation))

    @property
    def references(self) -> Sequence[SymbolReference]:
        return [self._symbol_reference] + list(self._accumulated_elements.references)

    @property
    def validator(self) -> SdvValidator:
        return sdv_validation.all_of([
            _ValidatorOfReferredProgram(self._symbol_name),
            self._accumulated_elements.validator,
        ])

    def resolve(self, symbols: SymbolTable) -> ProgramDdv:
        program_of_symbol = lookups.lookup_program(symbols, self._symbol_name)
        acc = self._accumulated_elements
        accumulated_program = program_of_symbol.new_accumulated(acc.stdin,
                                                                acc.arguments,
                                                                acc.transformations,
                                                                acc.validators)
        assert isinstance(accumulated_program, ProgramSdv)  # Type info for IDE

        program_ddv = accumulated_program.resolve(symbols)

        assert isinstance(program_ddv, ProgramDdv)  # Type info for IDE

        return ProgramDdv(program_ddv.command,
                          program_ddv.stdin,
                          program_ddv.transformation)


def plain(symbol_name: str,
          arguments: ArgumentsSdv = arguments_sdvs.empty()) -> ProgramSdvForSymbolReference:
    return ProgramSdvForSymbolReference(symbol_name,
                                        accumulator.new_with_arguments(arguments))


class _ValidatorOfReferredProgram(SdvValidatorOfReferredSdvBase):
    def _referred_validator(self, environment: PathResolvingEnvironment) -> SdvValidator:
        program_of_symbol = lookups.lookup_program(environment.symbols, self.symbol_name)
        return program_of_symbol.validator
