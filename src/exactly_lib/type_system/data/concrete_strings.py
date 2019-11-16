from typing import Callable, Set

from exactly_lib.test_case_file_structure.dir_dependent_value import DependenciesAwareDdv, DirDependencies
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.data.list_ddv import ListDdv
from exactly_lib.type_system.data.path_ddv import PathDdv
from exactly_lib.type_system.data.string_ddv import StringFragmentDdv, StringDdv
from exactly_lib.util.render import strings, combinators as rend_comb
from exactly_lib.util.render.renderer import Renderer


class ConstantFragmentDdv(StringFragmentDdv):
    def __init__(self, string_constant: str):
        self.string_constant = string_constant

    def resolving_dependencies(self) -> set:
        return set()

    def has_dir_dependency(self) -> bool:
        return False

    def exists_pre_sds(self) -> bool:
        return True

    def value_when_no_dir_dependencies(self):
        return self.string_constant

    def value_of_any_dependency(self, tcds: Tcds) -> str:
        return self.string_constant

    def describer(self) -> Renderer[str]:
        return rend_comb.ConstantR(self.string_constant)

    def __str__(self):
        return '{}({})'.format('ConstantFragment',
                               repr(self.string_constant))


class _StringFragmentDdvFromDirDependentValue(StringFragmentDdv):
    def __init__(self, value: DependenciesAwareDdv):
        self.value = value

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return self.value.resolving_dependencies()

    def has_dir_dependency(self) -> bool:
        return self.value.has_dir_dependency()

    def exists_pre_sds(self) -> bool:
        return self.value.exists_pre_sds()

    def value_when_no_dir_dependencies(self):
        return self._to_string(self.value.value_when_no_dir_dependencies())

    def value_of_any_dependency(self, tcds: Tcds) -> str:
        return self._to_string(self.value.value_of_any_dependency(tcds))

    def _to_string(self, x) -> str:
        raise NotImplementedError()


class StringDdvFragmentDdv(_StringFragmentDdvFromDirDependentValue):
    def __init__(self, string: StringDdv):
        super().__init__(string)
        self._string = string

    def describer(self) -> Renderer[str]:
        return self._string.describer()

    def _to_string(self, value) -> str:
        return value

    def __str__(self):
        return '{}({})'.format('StringValueFragment',
                               repr(self.value))


class ListFragmentDdv(_StringFragmentDdvFromDirDependentValue):
    def __init__(self, list_value: ListDdv):
        super().__init__(list_value)
        self._list = list_value

    def describer(self) -> Renderer[str]:
        return strings.JoiningOfElementsRenderer(self._list.describer(),
                                                 rend_comb.ConstantR(' '))

    def _to_string(self, value) -> str:
        return ' '.join(value)

    def __str__(self):
        return '{}({})'.format('ListValueFragment',
                               repr(self.value))


class PathFragmentDdv(_StringFragmentDdvFromDirDependentValue):
    def __init__(self, path: PathDdv):
        super().__init__(path)
        self._path = path

    def describer(self) -> Renderer[str]:
        return self._path.describer().value

    def _to_string(self, value) -> str:
        return str(value)

    def __str__(self):
        return '{}({})'.format('PathFragment',
                               repr(self.value))


StrValueTransformer = Callable[[str], str]


class TransformedStringFragmentDdv(StringFragmentDdv):
    def __init__(self,
                 string_fragment: StringFragmentDdv,
                 transformer: StrValueTransformer):
        self._string_fragment = string_fragment
        self._transformer = transformer

    def dir_dependencies(self) -> DirDependencies:
        return self._string_fragment.dir_dependencies()

    def has_dir_dependency(self) -> bool:
        return self._string_fragment.has_dir_dependency()

    def resolving_dependencies(self) -> set:
        return self._string_fragment.resolving_dependencies()

    def exists_pre_sds(self) -> bool:
        return self._string_fragment.exists_pre_sds()

    def value_when_no_dir_dependencies(self) -> str:
        return self._transformer(self._string_fragment.value_when_no_dir_dependencies())

    def value_of_any_dependency(self, tcds: Tcds) -> str:
        return self._transformer(self._string_fragment.value_of_any_dependency(tcds))

    def describer(self) -> Renderer[str]:
        return _TransformedStringRenderer(self._string_fragment,
                                          self._transformer)


def string_ddv_of_single_string(value: str) -> StringDdv:
    return StringDdv((ConstantFragmentDdv(value),))


def string_ddv_of_single_path(path: PathDdv) -> StringDdv:
    return StringDdv((PathFragmentDdv(path),))


class _TransformedStringRenderer(Renderer[str]):
    def __init__(self,
                 string_fragment: StringFragmentDdv,
                 transformer: StrValueTransformer):
        self._string_fragment = string_fragment
        self._transformer = transformer

    def render(self) -> str:
        un_transformed = self._string_fragment.describer().render()
        return self._transformer(un_transformed)
