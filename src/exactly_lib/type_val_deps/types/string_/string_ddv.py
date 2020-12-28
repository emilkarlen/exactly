from abc import ABC, abstractmethod
from typing import Sequence, Set

from exactly_lib.tcfs.path_relativity import DirectoryStructurePartition
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.ddv import resolving_deps_utils
from exactly_lib.type_val_deps.dep_variants.ddv.dir_dependent_value import MultiDependenciesDdv
from exactly_lib.util.render import strings
from exactly_lib.util.render.renderer import Renderer


class StringWithDirDependency(MultiDependenciesDdv[str]):
    pass


class StringFragmentDdv(StringWithDirDependency, ABC):
    """
    A fragment that, together with other fragments, makes up a `StringValue`
    """

    @abstractmethod
    def describer(self) -> Renderer[str]:
        """Rendition for presentation in error messages etc"""
        pass


class StringDdv(StringWithDirDependency):
    def __init__(self, fragments: Sequence[StringFragmentDdv]):
        self._fragments = fragments

    @property
    def fragments(self) -> Sequence[StringFragmentDdv]:
        return self._fragments

    def describer(self) -> Renderer[str]:
        return strings.JoiningOfElementRenderers([
            fragment.describer()
            for fragment in self._fragments
        ])

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return resolving_deps_utils.resolving_dependencies_from_sequence(self._fragments)

    def value_when_no_dir_dependencies(self) -> str:
        fragment_strings = [f.value_when_no_dir_dependencies()
                            for f in self._fragments]
        return ''.join(fragment_strings)

    def value_of_any_dependency(self, tcds: TestCaseDs) -> str:
        fragment_strings = [f.value_of_any_dependency(tcds)
                            for f in self._fragments]
        return ''.join(fragment_strings)

    def __str__(self):
        return '{}([{}])'.format('StringValue',
                                 ','.join(map(str, self._fragments)))
