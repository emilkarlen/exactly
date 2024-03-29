from typing import Sequence, List

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.string_transformer.test_resources import argument_syntax
from exactly_lib_test.type_val_deps.dep_variants.ddv.test_resources import ddv_validators
from exactly_lib_test.type_val_deps.test_resources.validation import validation
from exactly_lib_test.type_val_deps.test_resources.validation.validation import ValidationAssertions, ValidationActual, \
    Expectation
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.string_transformers import \
    string_transformer_from_primitive_value
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerSymbolContext


class ValidationCase:
    def __init__(self,
                 symbol_name: str,
                 expectation: ValidationAssertions,
                 actual: ValidationActual,
                 ):
        self.actual = actual
        self._expectation = expectation
        self._symbol_context = StringTransformerSymbolContext.of_sdv(
            symbol_name,
            string_transformer_from_primitive_value(
                validator=ddv_validators.constant(actual)
            )
        )
        self._expectation__bool = Expectation.corresponding_to(actual)

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
