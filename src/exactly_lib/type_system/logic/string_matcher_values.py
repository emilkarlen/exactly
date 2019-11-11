from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.string_matcher import StringMatcherValue, StringMatcher


class StringMatcherConstantValue(StringMatcherValue):
    """
    A :class:`StringMatcherValue` that is a constant :class:`StringMatcher`
    """

    def __init__(self, value: StringMatcher):
        self._value = value

    def structure(self) -> StructureRenderer:
        return self._value.structure()

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> StringMatcher:
        return self._value
