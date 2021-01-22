from typing import Sequence

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.string_transformers.test_resources import argument_syntax
from exactly_lib_test.impls.types.test_resources import validation
from exactly_lib_test.impls.types.test_resources.pre_or_post_sds_value_validator import constant_validator
from exactly_lib_test.impls.types.test_resources.validation import ValidationAssertions, ValidationActual
from exactly_lib_test.type_val_deps.types.test_resources.line_matcher import LineMatcherSymbolContext, \
    sdv_from_primitive_value


class ValidationCase:
    def __init__(self,
                 expectation: ValidationAssertions,
                 actual: ValidationActual,
                 ):
        self._expectation = expectation
        self._symbol_context = LineMatcherSymbolContext.of_sdv(
            'line_matcher_symbol',
            sdv_from_primitive_value(
                validator=constant_validator(actual)
            )
        )

    @property
    def transformer_arguments_string(self) -> str:
        return argument_syntax.syntax_for_transformer_option(
            self._symbol_context.name
        )

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