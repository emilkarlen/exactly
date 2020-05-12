from typing import Sequence, List

from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib.type_system.logic.file_matcher import FileMatcher, GenericFileMatcherSdv
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources.file_matcher import FileMatcherSymbolContext
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import arrangement_wo_tcds, \
    PrimAndExeExpectation, Arrangement
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_case_utils.test_resources.pre_or_post_sds_value_validator import constant_validator
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationActual, \
    ValidationExpectationSvh, ValidationAssertions
from exactly_lib_test.test_resources.test_utils import NExArr


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
        for case in validation.failing_validation_cases__svh()
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


def _successful_matcher_with_validation(the_validation: ValidationActual) -> GenericFileMatcherSdv:
    def get_matcher(symbols: SymbolTable, tcds: Tcds) -> FileMatcher:
        return constant.MatcherWithConstantResult(True)

    return matchers.sdv_from_parts(
        references=(),
        validator=constant_validator(the_validation),
        matcher=get_matcher
    )
