from exactly_lib.type_system.logic.string_matcher import StringMatcher, StringMatcherModel


class StringMatcherConstant(StringMatcher):
    """Matcher with constant result."""

    def __init__(self, result: bool):
        self._result = result

    @property
    def option_description(self) -> str:
        return 'any string' if self._result else 'no string'

    @property
    def result_constant(self) -> bool:
        return self._result

    def matches(self, model: StringMatcherModel) -> bool:
        return self._result
