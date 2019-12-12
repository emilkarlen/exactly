from typing import Sequence

from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib.test_case_utils.matcher.impls import sdv_components
from exactly_lib.test_case_utils.string_matcher import delegated_matcher
from exactly_lib_test.symbol.test_resources.string_matcher import StringMatcherSymbolContext
from exactly_lib_test.test_case_utils.matcher.test_resources import matchers
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_case_utils.test_resources.pre_or_post_sds_validator import constant_ddv_validator
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationExpectation, ValidationActual
from exactly_lib_test.test_resources.name_and_value import NameAndValue


class ValidationCase:
    def __init__(self,
                 expectation: ValidationExpectation,
                 actual: ValidationActual,
                 ):
        self._expectation = expectation
        self._symbol_context = StringMatcherSymbolContext(
            'string_matcher_symbol',
            delegated_matcher.StringMatcherSdvDelegatedToMatcher(
                sdv_components.MatcherSdvFromConstantDdv(
                    matchers.MatcherDdvOfConstantMatcherTestImpl(
                        constant.MatcherWithConstantResult(True),
                        validator=constant_ddv_validator(actual)

                    )
                ),
            )
        )

    @property
    def symbol_context(self) -> StringMatcherSymbolContext:
        return self._symbol_context

    @property
    def expectation(self) -> ValidationExpectation:
        return self._expectation


def failing_validation_cases() -> Sequence[NameAndValue[ValidationCase]]:
    return [
        NameAndValue(
            case.name,
            ValidationCase(case.expected,
                           case.actual)
        )
        for case in validation.failing_validation_cases()
    ]
