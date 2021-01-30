from typing import Sequence, List

from exactly_lib.impls.types.matcher.impls import constant
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.types.file_matcher import FileMatcherSdv
from exactly_lib.type_val_prims.matcher.file_matcher import FileMatcher
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.test_resources.validation import ddv_validators, validation
from exactly_lib_test.impls.test_resources.validation import svh_validation
from exactly_lib_test.impls.test_resources.validation.svh_validation import ValidationExpectationSvh
from exactly_lib_test.impls.test_resources.validation.validation import ValidationActual, \
    ValidationAssertions
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Arrangement, arrangement_wo_tcds, \
    PrimAndExeExpectation
from exactly_lib_test.impls.types.matcher.test_resources import sdv_ddv
from exactly_lib_test.impls.types.string_transformer.test_resources import argument_syntax
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.type_val_deps.types.test_resources.file_matcher import FileMatcherSymbolContext


class ValidationCaseSvh:
    def __init__(self,
                 symbol_name: str,
                 expectation: ValidationExpectationSvh,
                 actual: ValidationActual,
                 ):
        self._expectation = expectation
        self._symbol_context = FileMatcherSymbolContext.of_sdv(
            symbol_name,
            _successful_matcher_with_validation(actual)
        )

    @property
    def transformer_arguments_string(self) -> str:
        return argument_syntax.syntax_for_transformer_option(
            self._symbol_context.name
        )

    @property
    def transformer_arguments_elements(self) -> List[str]:
        return argument_syntax.arguments_for_transformer_option(
            self._symbol_context.name
        )

    @property
    def symbol_context(self) -> FileMatcherSymbolContext:
        return self._symbol_context

    @property
    def expectation(self) -> ValidationExpectationSvh:
        return self._expectation


def failing_validation_cases__svh(symbol_name: str = 'file_matcher_symbol'
                                  ) -> Sequence[NameAndValue[ValidationCaseSvh]]:
    return [
        NameAndValue(
            case.name,
            ValidationCaseSvh(symbol_name,
                              case.expected,
                              case.actual)
        )
        for case in svh_validation.failing_validation_cases__svh()
    ]


class ValidationCase:
    def __init__(self,
                 expectation: ValidationAssertions,
                 actual: ValidationActual,
                 symbol_name: str = 'file_matcher_symbol',
                 ):
        self._expectation = expectation
        self._symbol_context = FileMatcherSymbolContext.of_sdv(
            symbol_name,
            _successful_matcher_with_validation(actual),
        )

    @property
    def symbol_context(self) -> FileMatcherSymbolContext:
        return self._symbol_context

    @property
    def expectation(self) -> ValidationAssertions:
        return self._expectation


def failing_validation_cases(symbol_name: str = 'file_matcher_symbol') -> Sequence[NameAndValue[ValidationCase]]:
    return [
        NameAndValue(
            case.name,
            ValidationCase(case.expected,
                           case.actual,
                           symbol_name)
        )
        for case in validation.failing_validation_cases()
    ]


def failing_validation_cases__multi_exe(symbol_name: str = 'files_matcher_symbol'
                                        ) -> Sequence[NExArr[PrimAndExeExpectation, Arrangement]]:
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


def _successful_matcher_with_validation(the_validation: ValidationActual) -> FileMatcherSdv:
    def get_matcher(symbols: SymbolTable, tcds: TestCaseDs) -> FileMatcher:
        return constant.MatcherWithConstantResult(True)

    return sdv_ddv.sdv_from_parts(
        references=(),
        validator=ddv_validators.constant(the_validation),
        matcher=get_matcher
    )
