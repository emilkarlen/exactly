from typing import Iterable, Set

from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.path_relativity import ResolvingDependency


def resolving_dependencies_from_sequence(dir_dependent_values: Iterable[DirDependentValue]) -> Set[ResolvingDependency]:
    ret_val = set()
    for value in dir_dependent_values:
        ret_val.update(value.resolving_dependencies())
    return ret_val
