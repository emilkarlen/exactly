from exactly_lib.test_case.validation.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.string_transformer.impl import select
from exactly_lib.type_system.logic.line_matcher import LineMatcherValue
from exactly_lib.type_system.logic.string_transformer import StringTransformerValue, StringTransformer


class SelectStringTransformerValue(StringTransformerValue):
    """
    Keeps lines matched by a given Line Matcher
    and discards lines not matched.
    """

    def __init__(self, line_matcher: LineMatcherValue):
        self._line_matcher = line_matcher

    def validator(self) -> PreOrPostSdsValueValidator:
        return self._line_matcher.validator

    def value_of_any_dependency(self, tcds: HomeAndSds) -> StringTransformer:
        return select.SelectStringTransformer(
            self._line_matcher.value_of_any_dependency(tcds))
