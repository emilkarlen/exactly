from typing import Sequence, Set

from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system import utils


class StringWithDirDependency(MultiDirDependentValue[str]):
    pass


class StringFragment(StringWithDirDependency):
    """
    A fragment that, together with other fragments, makes up a `StringValue`
    """
    pass


class StringValue(StringWithDirDependency):
    def __init__(self, fragments: Sequence[StringFragment]):
        self._fragments = fragments

    @property
    def fragments(self) -> Sequence[StringFragment]:
        return self._fragments

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return utils.resolving_dependencies_from_sequence(self._fragments)

    def value_when_no_dir_dependencies(self) -> str:
        fragment_strings = [f.value_when_no_dir_dependencies()
                            for f in self._fragments]
        return ''.join(fragment_strings)

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> str:
        fragment_strings = [f.value_of_any_dependency(home_and_sds)
                            for f in self._fragments]
        return ''.join(fragment_strings)

    def __str__(self):
        return '{}([{}])'.format('StringValue',
                                 ','.join(map(str, self._fragments)))
