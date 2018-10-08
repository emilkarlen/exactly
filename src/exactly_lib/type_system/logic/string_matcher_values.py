from typing import Set, Callable

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.logic.string_matcher import StringMatcherValue, StringMatcher


class StringMatcherConstantValue(StringMatcherValue):
    """
    A :class:`StringMatcherValue` that is a constant :class:`StringMatcher`
    """

    def __init__(self, value: StringMatcher):
        self._value = value

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> StringMatcher:
        return self._value


class DirDependentStringMatcherValue(StringMatcherValue):
    def __init__(self,
                 dependencies: Set[DirectoryStructurePartition],
                 constructor: Callable[[HomeAndSds], StringMatcher]):
        self._constructor = constructor
        self._dependencies = dependencies

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self._dependencies

    def exists_pre_sds(self) -> bool:
        return DirectoryStructurePartition.NON_HOME not in self.resolving_dependencies()

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> StringMatcher:
        return self._constructor(home_and_sds)
