import functools
from typing import Set, Iterable, Sequence

from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import ResolvingDependency
from exactly_lib.util.functional import compose_first_and_second


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


class IdentityLinesTransformer(LinesTransformer):
    @property
    def is_identity_transformer(self) -> bool:
        return True

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        return lines


class SequenceLinesTransformer(LinesTransformer):
    def __init__(self, transformers: Sequence[LinesTransformer]):
        self._transformers = tuple(transformers)

    @property
    def is_identity_transformer(self) -> bool:
        return all([t.is_identity_transformer for t in self._transformers])

    @property
    def transformers(self) -> Sequence[LinesTransformer]:
        return self._transformers

    def transform(self, lines: Iterable[str]) -> Iterable[str]:
        if not self._transformers:
            return lines
        else:
            return self._sequenced_transformers()(lines)

    def _sequenced_transformers(self):
        lines_to_lines_transformers = [t.transform
                                       for t in self._transformers]

        return functools.reduce(compose_first_and_second, lines_to_lines_transformers)

    def __str__(self):
        return '{}[{}]'.format(type(self).__name__,
                               ','.join(map(str, self._transformers)))


class CustomLinesTransformer(LinesTransformer):
    """
    Base class for built in custom transformers.
    """

    def __str__(self):
        return str(type(self))
