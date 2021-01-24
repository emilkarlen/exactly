from typing import Sequence

from exactly_lib.impls.types.string_transformer.sdvs import StringTransformerSdvReference
from exactly_lib.type_val_deps.types.program.sdv.accumulated_components import AccumulatedComponents
from exactly_lib.type_val_deps.types.string_ import string_sdvs
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.test_resources.validation.svh_validation import ValidationExpectationSvh
from exactly_lib_test.impls.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Arrangement, arrangement_wo_tcds, \
    PrimAndExeExpectation
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.impls.types.program.test_resources import arguments_building as args
from exactly_lib_test.impls.types.program.test_resources import program_sdvs
from exactly_lib_test.impls.types.string_transformers.test_resources import \
    validation_cases as str_trans_validation_cases
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext


class ValidationCase:
    def __init__(self,
                 symbol_name: str,
                 string_transformer_case: str_trans_validation_cases.ValidationCase,
                 ):
        self._string_transformer_case = string_transformer_case
        additional_components = AccumulatedComponents.of_transformation(
            StringTransformerSdvReference(string_transformer_case.symbol_context.name)
        )
        program_w_transformer = program_sdvs.system_program(
            string_sdvs.str_constant('system-program')
        ).new_accumulated(additional_components)

        self._program_symbol_context = ProgramSymbolContext.of_sdv(
            symbol_name,
            program_w_transformer
        )

    @property
    def argument_elements(self) -> ArgumentElements:
        return args.symbol_ref_command_elements(self._program_symbol_context.name)

    @property
    def program_symbol_context(self) -> ProgramSymbolContext:
        return self._program_symbol_context

    @property
    def symbol_contexts(self) -> Sequence[SymbolContext]:
        return [
            self._program_symbol_context,
            self._string_transformer_case.symbol_context,
        ]

    @property
    def symbol_table(self) -> SymbolTable:
        return SymbolContext.symbol_table_of_contexts(self.symbol_contexts)

    @property
    def expectation(self) -> ValidationAssertions:
        return self._string_transformer_case.expectation

    @property
    def expectation__svh(self) -> ValidationExpectationSvh:
        return ValidationExpectationSvh.of_plain(self._string_transformer_case.expectation__bool)


def failing_validation_cases(symbol_name: str = 'program_symbol',
                             string_transformer_symbol_name: str = 'string_transformer_symbol',
                             ) -> Sequence[NameAndValue[ValidationCase]]:
    return [
        NameAndValue(
            case.name,
            ValidationCase(symbol_name,
                           case.value)
        )
        for case in str_trans_validation_cases.failing_validation_cases(string_transformer_symbol_name)
    ]


def validation_exe_case(case: NameAndValue[ValidationCase]) -> NExArr[PrimAndExeExpectation, Arrangement]:
    return NExArr(
        case.name,
        PrimAndExeExpectation.of_exe(
            validation=case.value.expectation,
        ),
        arrangement_wo_tcds(
            symbols=case.value.symbol_table,
        )
    )
