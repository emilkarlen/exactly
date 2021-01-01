from typing import Sequence

from exactly_lib.impls.types.matcher.impls import constant
from exactly_lib.impls.types.matcher.impls import sdv_components
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.matcher.test_resources import sdv_ddv
from exactly_lib_test.impls.types.test_resources import validation
from exactly_lib_test.impls.types.test_resources.pre_or_post_sds_validator import constant_ddv_validator
from exactly_lib_test.impls.types.test_resources.validation import ValidationAssertions, ValidationActual
from exactly_lib_test.type_val_deps.types.test_resources.string_matcher import StringMatcherSymbolContext


class ValidationCase:
    def __init__(self,
                 expectation: ValidationAssertions,
                 actual: ValidationActual,
                 ):
        self._expectation = expectation
        self._symbol_context = StringMatcherSymbolContext.of_sdv(
            'string_matcher_symbol',
            sdv_components.MatcherSdvFromConstantDdv(
                sdv_ddv.MatcherDdvOfConstantMatcherTestImpl(
                    constant.MatcherWithConstantResult(True),
                    validator=constant_ddv_validator(actual)

                )
            )
        )

    @property
    def symbol_context(self) -> StringMatcherSymbolContext:
        return self._symbol_context

    @property
    def expectation(self) -> ValidationAssertions:
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
