from typing import Sequence

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.test_resources.validation import validation
from exactly_lib_test.impls.test_resources.validation.ddv_validators import DdvValidatorThat
from exactly_lib_test.impls.test_resources.validation.svh_validation import ValidationExpectationSvh
from exactly_lib_test.impls.test_resources.validation.validation import ValidationAssertions, ValidationActual
from exactly_lib_test.impls.types.matcher.test_resources import sdv_ddv
from exactly_lib_test.type_val_deps.types.integer_matcher.test_resources.abstract_syntax import IntegerMatcherAbsStx
from exactly_lib_test.type_val_deps.types.integer_matcher.test_resources.symbol_context import \
    IntegerMatcherSymbolContext


class ValidationCase:
    def __init__(self,
                 symbol_name: str,
                 actual: ValidationActual,
                 ):
        self.actual = actual
        self._symbol_context = IntegerMatcherSymbolContext.of_sdv(
            symbol_name,
            sdv_ddv.sdv_from_primitive_value(
                validator=DdvValidatorThat.corresponding_to(actual)
            )
        )

    @property
    def abstract_syntax(self) -> IntegerMatcherAbsStx:
        return self._symbol_context.abstract_syntax

    @property
    def symbol_context(self) -> IntegerMatcherSymbolContext:
        return self._symbol_context

    @property
    def symbol_table(self) -> SymbolTable:
        return self.symbol_context.symbol_table

    @property
    def expectation(self) -> ValidationAssertions:
        return ValidationAssertions.corresponding_to(self.actual)

    @property
    def expectation__svh(self) -> ValidationExpectationSvh:
        return ValidationExpectationSvh.corresponding_to(self.actual)


def failing_validation_cases(symbol_name: str = 'INTEGER_MATCHER_SYMBOL',
                             ) -> Sequence[NameAndValue[ValidationCase]]:
    return [
        NameAndValue(
            case.name,
            ValidationCase(symbol_name,
                           case.actual)
        )
        for case in validation.failing_validation_cases()
    ]
