from typing import Sequence, List

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.symbol.logic.test_resources.string_transformer.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.symbol.test_resources.string_transformer import string_transformer_from_primitive_value
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_case_utils.test_resources.pre_or_post_sds_value_validator import constant_validator
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationAssertions, ValidationActual, \
    Expectation


class ValidationCase:
    def __init__(self,
                 symbol_name: str,
                 expectation: ValidationAssertions,
                 actual: ValidationActual,
                 ):
        self._expectation = expectation
        self._symbol_context = StringTransformerSymbolContext.of_sdv(
            symbol_name,
            string_transformer_from_primitive_value(
                validator=constant_validator(actual)
            )
        )
        self._expectation__bool = Expectation(
            passes_pre_sds=actual.pre_sds is None,
            passes_post_sds=actual.post_sds is None,
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
    def symbol_context(self) -> StringTransformerSymbolContext:
        return self._symbol_context

    @property
    def expectation(self) -> ValidationAssertions:
        return self._expectation

    @property
    def expectation__bool(self) -> Expectation:
        return self._expectation__bool


def failing_validation_cases(symbol_name: str = 'string_transformer_symbol') -> Sequence[NameAndValue[ValidationCase]]:
    return [
        NameAndValue(
            case.name,
            ValidationCase(symbol_name,
                           case.expected,
                           case.actual)
        )
        for case in validation.failing_validation_cases()
    ]
