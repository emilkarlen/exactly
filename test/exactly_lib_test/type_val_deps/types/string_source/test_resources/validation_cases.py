from typing import Sequence

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.type_val_deps.dep_variants.ddv.test_resources import ddv_validators
from exactly_lib_test.type_val_deps.test_resources.validation import validation
from exactly_lib_test.type_val_deps.test_resources.validation.validation import ValidationAssertions, ValidationActual
from exactly_lib_test.type_val_deps.test_resources.validation_case import ValidationCaseWSymbolContextAndAssertion
from exactly_lib_test.type_val_deps.types.string_source.test_resources import sdvs, ddvs
from exactly_lib_test.type_val_deps.types.string_source.test_resources.symbol_context import StringSourceSymbolContext


class ValidationCase(ValidationCaseWSymbolContextAndAssertion):
    def __init__(self,
                 symbol_name: str,
                 actual: ValidationActual,
                 ):
        self._symbol_context = StringSourceSymbolContext.of_sdv(
            symbol_name,
            sdvs.StringSourceSdvConstantTestImpl(
                ddvs.StringSourceDdvWoResolvingTestImpl(
                    ddv_validators.constant(actual)
                )
            )
        )
        self.syntax = self._symbol_context.abstract_syntax
        self._expectation = validation.Expectation.corresponding_to(actual)
        self._assertions = ValidationAssertions.corresponding_to(actual)

    @property
    def symbol_context(self) -> StringSourceSymbolContext:
        return self._symbol_context

    @property
    def expectation(self) -> validation.Expectation:
        return self._expectation

    @property
    def assertion(self) -> ValidationAssertions:
        return self._assertions


def failing_validation_cases(symbol_name: str = 'STRING_SOURCE_SYMBOL') -> Sequence[NameAndValue[ValidationCase]]:
    return [
        NameAndValue(
            case.name,
            ValidationCase(symbol_name,
                           case.actual)
        )
        for case in validation.failing_validation_cases()
    ]
