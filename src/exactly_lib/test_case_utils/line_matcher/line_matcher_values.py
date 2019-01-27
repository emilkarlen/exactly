from typing import Set

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.logic.line_matcher import LineMatcher, LineMatcherValue


class LineMatcherValueFromPrimitiveValue(LineMatcherValue):
    def __init__(self, primitive_value: LineMatcher):
        self._primitive_value = primitive_value

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return set()

    def value_when_no_dir_dependencies(self) -> LineMatcher:
        return self._primitive_value

    def value_of_any_dependency(self, tcds: HomeAndSds) -> LineMatcher:
        return self._primitive_value
