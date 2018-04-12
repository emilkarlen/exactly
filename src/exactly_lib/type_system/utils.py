from typing import Iterable, Set, TypeVar

from exactly_lib.test_case_file_structure.dir_dependent_value import WithDirDependencies
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition


def resolving_dependencies_from_sequence(dir_dependent_values: Iterable[WithDirDependencies]) -> Set[
    DirectoryStructurePartition]:
    return unions(map(lambda value: value.resolving_dependencies(),
                      dir_dependent_values))


T = TypeVar('T')


def unions(sets: Iterable[Set[T]]) -> Set[T]:
    ret_val = set()
    for s in sets:
        ret_val.update(s)
    return ret_val
