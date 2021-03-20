from typing import Sequence

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.string_transformer.test_resources import argument_syntax
from exactly_lib_test.type_val_deps.dep_variants.ddv.test_resources import ddv_validators
from exactly_lib_test.type_val_deps.test_resources.validation import validation
from exactly_lib_test.type_val_deps.test_resources.validation.validation import ValidationAssertions, ValidationActual
from exactly_lib_test.type_val_deps.types.line_matcher.test_resources.abstract_syntax import LineMatcherAbsStx
from exactly_lib_test.type_val_deps.types.line_matcher.test_resources.line_matchers import sdv_from_primitive_value
from exactly_lib_test.type_val_deps.types.line_matcher.test_resources.symbol_context import LineMatcherSymbolContext


class ValidationCase:
    def __init__(self,
                 expectation: ValidationAssertions,
                 actual: ValidationActual,
                 ):
        self._expectation = expectation
        self._symbol_context = LineMatcherSymbolContext.of_sdv(
            'line_matcher_symbol',
            sdv_from_primitive_value(
                validator=ddv_validators.constant(actual)
            )
        )

    @property
    def transformer_arguments_string(self) -> str:
        return argument_syntax.syntax_for_transformer_option(
            self._symbol_context.name
        )

    @property
    def matcher_abs_stx(self) -> LineMatcherAbsStx:
        return self._symbol_context.abstract_syntax

    @property
    def symbol_context(self) -> LineMatcherSymbolContext:
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
