from typing import Optional

from exactly_lib.type_system.error_message import ErrorMessageResolver
from exactly_lib.type_system.logic.string_matcher import StringMatcher, FileToCheck
from exactly_lib.type_system.logic.string_transformer import StringTransformer


class StringMatcherConstant(StringMatcher):
    """Matcher with constant result."""

    def __init__(self, result: Optional[ErrorMessageResolver]):
        self._result = result

    @property
    def option_description(self) -> str:
        return 'any string' if self._result else 'no string'

    @property
    def result_constant(self) -> Optional[ErrorMessageResolver]:
        return self._result

    def matches(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        return self._result


class StringMatcherOnTransformedFileToCheck(StringMatcher):
    """Applies a string transformer to the file to check."""

    def __init__(self,
                 transformer: StringTransformer,
                 on_transformed: StringMatcher):
        self._transformer = transformer
        self._on_transformed = on_transformed

    @property
    def option_description(self) -> str:
        return 'transformed: ' + self._on_transformed.option_description

    def matches(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        transformed_model = model.with_transformation(self._transformer)
        return self._on_transformed.matches(transformed_model)
