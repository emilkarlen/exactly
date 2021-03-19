from typing import Sequence

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.test_resources.validation import ddv_validators, validation
from exactly_lib_test.impls.test_resources.validation.validation import ValidationActual, ValidationAssertions
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_wo_tcds, \
    PrimAndExeExpectation
from exactly_lib_test.impls.types.matcher.test_resources import sdv_ddv
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.type_val_deps.types.files_matcher.test_resources.symbol_context import FilesMatcherSymbolContext


class ValidationCase:
    def __init__(self,
                 expectation: ValidationAssertions,
                 actual: ValidationActual,
                 symbol_name: str = 'files_matcher_symbol',
                 ):
        self._expectation = expectation
        self._symbol_context = FilesMatcherSymbolContext.of_sdv(
            symbol_name,
            sdv_ddv.sdv_from_bool(
                True,
                validator=ddv_validators.constant(actual),
            ),
        )

    @property
    def symbol_context(self) -> FilesMatcherSymbolContext:
        return self._symbol_context

    @property
    def expectation(self) -> ValidationAssertions:
        return self._expectation


def failing_validation_cases(symbol_name: str = 'files_matcher_symbol'
                             ) -> Sequence[NameAndValue[ValidationCase]]:
    return [
        NameAndValue(
            case.name,
            ValidationCase(case.expected,
                           case.actual,
                           symbol_name)
        )
        for case in validation.failing_validation_cases()
    ]


def failing_validation_cases__multi_exe(symbol_name: str = 'files_matcher_symbol'):
    return [
        NExArr(
            case.name,
            PrimAndExeExpectation.of_exe(
                validation=case.value.expectation,
            ),
            arrangement_wo_tcds(
                symbols=case.value.symbol_context.symbol_table,
            ),
        )
        for case in failing_validation_cases(symbol_name)
    ]
