from typing import Sequence

from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib_test.symbol.test_resources.files_matcher import is_reference_to_files_matcher__ref, \
    files_matcher_sdv_constant_test_impl
from exactly_lib_test.symbol.test_resources.symbols_setup import SdvSymbolContext
from exactly_lib_test.test_case_utils.test_resources import pre_or_post_sds_value_validator
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationActual, ValidationExpectation
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class FilesMatcherSymbolContext(SdvSymbolContext[FilesMatcherSdv]):
    def __init__(self,
                 name: str,
                 sdv: FilesMatcherSdv):
        super().__init__(name)
        self._sdv = sdv

    @property
    def sdv(self) -> FilesMatcherSdv:
        return self._sdv

    @property
    def reference_assertion(self) -> ValueAssertion[SymbolReference]:
        return is_reference_to_files_matcher__ref(self.name)


class ValidationCase:
    def __init__(self,
                 expectation: ValidationExpectation,
                 actual: ValidationActual,
                 symbol_name: str = 'files_matcher_symbol',
                 ):
        self._expectation = expectation
        self._symbol_context = FilesMatcherSymbolContext(
            symbol_name,
            files_matcher_sdv_constant_test_impl(
                True,
                validator=pre_or_post_sds_value_validator.constant_validator(actual),
            ),
        )

    @property
    def symbol_context(self) -> FilesMatcherSymbolContext:
        return self._symbol_context

    @property
    def expectation(self) -> ValidationExpectation:
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
