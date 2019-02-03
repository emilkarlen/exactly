from typing import Sequence, List

from exactly_lib_test.symbol.test_resources.string_transformer import StringTransformerSymbolContext, \
    string_transformer_from_primitive_value
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax
from exactly_lib_test.test_case_utils.test_resources import validation
from exactly_lib_test.test_case_utils.test_resources.pre_or_post_sds_value_validator import constant_validator
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationExpectation, ValidationActual
from exactly_lib_test.test_resources.name_and_value import NameAndValue


class ValidationCase:
    def __init__(self,
                 symbol_name: str,
                 expectation: ValidationExpectation,
                 actual: ValidationActual,
                 ):
        self._expectation = expectation
        self._symbol_context = StringTransformerSymbolContext(
            symbol_name,
            string_transformer_from_primitive_value(
                validator=constant_validator(actual)
            )
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
    def expectation(self) -> ValidationExpectation:
        return self._expectation


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
