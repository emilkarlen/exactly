from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.data.list_value import ListValue
from exactly_lib.type_system.data.string_value import StringFragment, StringValue


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

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> str:
        return self.string_constant

    def __str__(self):
        return '{}({})'.format('ConstantFragment',
                               repr(self.string_constant))


class _StringFragmentFromDirDependentValue(StringFragment):
    def __init__(self, value: DirDependentValue):
        self.value = value

    def resolving_dependencies(self) -> set:
        return self.value.resolving_dependencies()

    def has_dir_dependency(self) -> bool:
        return self.value.has_dir_dependency()

    def exists_pre_sds(self) -> bool:
        return self.value.exists_pre_sds()

    def value_when_no_dir_dependencies(self):
        return self._to_string(self.value.value_when_no_dir_dependencies())

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> str:
        return self._to_string(self.value.value_of_any_dependency(home_and_sds))

    def _to_string(self, x) -> str:
        raise NotImplementedError()


class StringValueFragment(_StringFragmentFromDirDependentValue):
    def __init__(self, string_value: StringValue):
        super().__init__(string_value)

    def _to_string(self, value) -> str:
        return value

    def __str__(self):
        return '{}({})'.format('StringValueFragment',
                               repr(self.value))


class ListValueFragment(_StringFragmentFromDirDependentValue):
    def __init__(self, list_value: ListValue):
        super().__init__(list_value)

    def _to_string(self, value) -> str:
        return ' '.join(value)

    def __str__(self):
        return '{}({})'.format('ListValueFragment',
                               repr(self.value))


class FileRefFragment(_StringFragmentFromDirDependentValue):
    def __init__(self, file_ref: FileRef):
        super().__init__(file_ref)

    def _to_string(self, value) -> str:
        return str(value)

    def __str__(self):
        return '{}({})'.format('FileRefFragment',
                               repr(self.value))


def string_value_of_single_string(value: str) -> StringValue:
    return StringValue((ConstantFragment(value),))


def string_value_of_single_file_ref(value: FileRef) -> StringValue:
    return StringValue((FileRefFragment(value),))
