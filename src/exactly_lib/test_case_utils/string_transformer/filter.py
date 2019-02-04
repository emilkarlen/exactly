from typing import Set

from exactly_lib.test_case.pre_or_post_value_validation import PreOrPostSdsValueValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
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

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._line_matcher.resolving_dependencies()

    def validator(self) -> PreOrPostSdsValueValidator:
        return self._line_matcher.validator()

    def value_when_no_dir_dependencies(self) -> StringTransformer:
        return select.SelectStringTransformer(
            self._line_matcher.value_when_no_dir_dependencies())

    def value_of_any_dependency(self, tcds: HomeAndSds) -> StringTransformer:
        return select.SelectStringTransformer(
            self._line_matcher.value_of_any_dependency(tcds))
