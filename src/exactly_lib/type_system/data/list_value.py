from typing import List, Set, Sequence

from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDependenciesDdv
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system import utils
from exactly_lib.type_system.data.string_value import StringValue
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import SequenceRenderer


class ListValue(MultiDependenciesDdv[List[str]]):
    def __init__(self, string_value_elements: List[StringValue]):
        self._string_value_elements = tuple(string_value_elements)

    @staticmethod
    def empty() -> 'ListValue':
        return ListValue([])

    def describer(self) -> SequenceRenderer[str]:
        return rend_comb.SequenceR([
            element.describer()
            for element in self._string_value_elements
        ])

    @property
    def string_value_elements(self) -> Sequence[StringValue]:
        return self._string_value_elements

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return utils.resolving_dependencies_from_sequence(self._string_value_elements)

    def value_when_no_dir_dependencies(self) -> List[str]:
        """
        :rtype: List of `str`
        """
        return [e.value_when_no_dir_dependencies()
                for e in self._string_value_elements]

    def value_of_any_dependency(self, tcds: HomeAndSds) -> List[str]:
        """
        :rtype: List of `str`
        """
        return [e.value_of_any_dependency(tcds)
                for e in self._string_value_elements]

    def __str__(self):
        return '{}([{}])'.format('ListValue',
                                 ','.join(map(str, self._string_value_elements)))
