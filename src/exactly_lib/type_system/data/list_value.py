from typing import List, Set

from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system import utils
from exactly_lib.type_system.data.string_value import StringValue


class ListValue(MultiDirDependentValue[List[str]]):
    def __init__(self, string_value_elements: List[StringValue]):
        """
        :param string_value_elements: list of :class:`StringValue`
        """
        self._string_value_elements = tuple(string_value_elements)

    @property
    def string_value_elements(self) -> tuple:
        return self._string_value_elements

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return utils.resolving_dependencies_from_sequence(self._string_value_elements)

    def value_when_no_dir_dependencies(self) -> List[str]:
        """
        :rtype: List of `str`
        """
        return [e.value_when_no_dir_dependencies()
                for e in self._string_value_elements]

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> List[str]:
        """
        :rtype: List of `str`
        """
        return [e.value_of_any_dependency(home_and_sds)
                for e in self._string_value_elements]

    def __str__(self):
        return '{}([{}])'.format('ListValue',
                                 ','.join(map(str, self._string_value_elements)))


def empty() -> ListValue:
    return ListValue([]
                     )
