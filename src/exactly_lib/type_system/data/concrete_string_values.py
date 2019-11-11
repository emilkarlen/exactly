from typing import Callable, Set

from exactly_lib.test_case_file_structure.dir_dependent_value import DependenciesAwareDdv, DirDependencies
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.list_value import ListValue
from exactly_lib.type_system.data.string_value import StringFragment, StringValue
from exactly_lib.util.render import strings, combinators as rend_comb
from exactly_lib.util.render.renderer import Renderer


class ConstantFragment(StringFragment):
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

    def value_of_any_dependency(self, tcds: HomeAndSds) -> str:
        return self.string_constant

    def describer(self) -> Renderer[str]:
        return rend_comb.ConstantR(self.string_constant)

    def __str__(self):
        return '{}({})'.format('ConstantFragment',
                               repr(self.string_constant))


class _StringFragmentFromDirDependentValue(StringFragment):
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

    def value_of_any_dependency(self, tcds: HomeAndSds) -> str:
        return self._to_string(self.value.value_of_any_dependency(tcds))

    def _to_string(self, x) -> str:
        raise NotImplementedError()


class StringValueFragment(_StringFragmentFromDirDependentValue):
    def __init__(self, string_value: StringValue):
        super().__init__(string_value)
        self._string_value = string_value

    def describer(self) -> Renderer[str]:
        return self._string_value.describer()

    def _to_string(self, value) -> str:
        return value

    def __str__(self):
        return '{}({})'.format('StringValueFragment',
                               repr(self.value))


class ListValueFragment(_StringFragmentFromDirDependentValue):
    def __init__(self, list_value: ListValue):
        super().__init__(list_value)
        self._list_value = list_value

    def describer(self) -> Renderer[str]:
        return strings.JoiningOfElementsRenderer(self._list_value.describer(),
                                                 rend_comb.ConstantR(' '))

    def _to_string(self, value) -> str:
        return ' '.join(value)

    def __str__(self):
        return '{}({})'.format('ListValueFragment',
                               repr(self.value))


class FileRefFragment(_StringFragmentFromDirDependentValue):
    def __init__(self, file_ref: FileRef):
        super().__init__(file_ref)
        self._file_ref = file_ref

    def describer(self) -> Renderer[str]:
        return self._file_ref.describer().value

    def _to_string(self, value) -> str:
        return str(value)

    def __str__(self):
        return '{}({})'.format('FileRefFragment',
                               repr(self.value))


StrValueTransformer = Callable[[str], str]


class TransformedStringFragment(StringFragment):
    def __init__(self,
                 string_fragment: StringFragment,
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

    def value_of_any_dependency(self, tcds: HomeAndSds) -> str:
        return self._transformer(self._string_fragment.value_of_any_dependency(tcds))

    def describer(self) -> Renderer[str]:
        return _TransformedStringRenderer(self._string_fragment,
                                          self._transformer)


def string_value_of_single_string(value: str) -> StringValue:
    return StringValue((ConstantFragment(value),))


def string_value_of_single_file_ref(value: FileRef) -> StringValue:
    return StringValue((FileRefFragment(value),))


class _TransformedStringRenderer(Renderer[str]):
    def __init__(self,
                 string_fragment: StringFragment,
                 transformer: StrValueTransformer):
        self._string_fragment = string_fragment
        self._transformer = transformer

    def render(self) -> str:
        un_transformed = self._string_fragment.describer().render()
        return self._transformer(un_transformed)
