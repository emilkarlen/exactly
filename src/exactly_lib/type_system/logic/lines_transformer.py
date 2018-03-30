from typing import Set, Iterable

from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import ResolvingDependency


class LinesTransformer:
    """
    Transforms a sequence of lines, where each line is a string.
    """

    @property
    def is_identity_transformer(self) -> bool:
        """
        Tells if this transformer is the identity transformer
        """
        return False

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        raise NotImplementedError('abstract method')

    def __str__(self):
        return type(self).__name__


class LinesTransformerValue(MultiDirDependentValue[LinesTransformer]):
    def resolving_dependencies(self) -> Set[ResolvingDependency]:
        return set()

    def value_when_no_dir_dependencies(self) -> LinesTransformer:
        """
        :raises DirDependencyError: This value has dir dependencies.
        """
        raise NotImplementedError()

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> LinesTransformer:
        """Gives the value, regardless of actual dependency."""
        raise NotImplementedError()
