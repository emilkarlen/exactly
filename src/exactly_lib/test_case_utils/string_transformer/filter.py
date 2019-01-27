from typing import Set

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_utils.string_transformer import transformers
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

    def value_when_no_dir_dependencies(self) -> StringTransformer:
        return transformers.SelectStringTransformer(self._line_matcher.value_when_no_dir_dependencies())

    def value_of_any_dependency(self, tcds: HomeAndSds) -> StringTransformer:
        return transformers.SelectStringTransformer(self._line_matcher.value_of_any_dependency(tcds))
