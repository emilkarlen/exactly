from typing import Sequence

from exactly_lib_test.symbol.test_resources.string_matcher import StringMatcherSymbolContext, \
    StringMatcherResolverConstantTestImpl
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_case_utils.test_resources.pre_or_post_sds_validator import constant_validator
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationExpectation, ValidationActual
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.type_system.logic.test_resources.string_matchers import StringMatcherConstant


class ValidationCase:
    def __init__(self,
                 expectation: ValidationExpectation,
                 actual: ValidationActual,
                 ):
        self._expectation = expectation
        self._symbol_context = StringMatcherSymbolContext(
            'string_matcher_symbol',
            StringMatcherResolverConstantTestImpl(
                StringMatcherConstant(None),
                validator=constant_validator(actual)
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
