from typing import List, Set, Sequence

from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDependenciesDdv
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system import utils
from exactly_lib.type_system.data.string_ddv import StringDdv
from exactly_lib.util.render import combinators as rend_comb
from exactly_lib.util.render.renderer import SequenceRenderer


class ListDdv(MultiDependenciesDdv[List[str]]):
    def __init__(self, string_elements: List[StringDdv]):
        self._string_elements = tuple(string_elements)

    @staticmethod
    def empty() -> 'ListDdv':
        return ListDdv([])

    def describer(self) -> SequenceRenderer[str]:
        return rend_comb.SequenceR([
            element.describer()
            for element in self._string_elements
        ])

    @property
    def string_elements(self) -> Sequence[StringDdv]:
        return self._string_elements

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return utils.resolving_dependencies_from_sequence(self._string_elements)

    def value_when_no_dir_dependencies(self) -> List[str]:
        """
        :rtype: List of `str`
        """
        return [e.value_when_no_dir_dependencies()
                for e in self._string_elements]

    def value_of_any_dependency(self, tcds: Tcds) -> List[str]:
        """
        :rtype: List of `str`
        """
        return [e.value_of_any_dependency(tcds)
                for e in self._string_elements]

    def __str__(self):
        return '{}([{}])'.format('ListValue',
                                 ','.join(map(str, self._string_elements)))
