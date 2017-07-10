from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue, MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import ResolvingDependency


class StringWithDirDependency(MultiDirDependentValue):
    pass


class StringFragment(StringWithDirDependency):
    """
    A fragment that, together with other fragments, makes up a `StringValue`
    """
    pass


class StringValue(StringWithDirDependency):
    def __init__(self, fragments: tuple):
        self._fragments = fragments

    @property
    def fragments(self) -> tuple:
        return self._fragments

    def resolving_dependencies(self) -> set:
        ret_val = set()
        for fragment in self._fragments:
            ret_val.update(fragment.resolving_dependencies())
        return ret_val

    def has_dir_dependency(self) -> bool:
        return bool(self.resolving_dependencies())

    def exists_pre_sds(self) -> bool:
        return ResolvingDependency.NON_HOME not in self.resolving_dependencies()

    def value_when_no_dir_dependencies(self):
        fragment_strings = [f.value_when_no_dir_dependencies()
                            for f in self._fragments]
        return ''.join(fragment_strings)

    # def value_pre_sds(self, home_dir_path: pathlib.Path) -> str:
    #     fragment_strings = [f.value_pre_sds(home_dir_path)
    #                         for f in self._fragments]
    #     return ''.join(fragment_strings)
    #
    # def value_post_sds(self, sds: SandboxDirectoryStructure) -> str:
    #     fragment_strings = [f.value_post_sds(sds)
    #                         for f in self._fragments]
    #     return ''.join(fragment_strings)

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> str:
        fragment_strings = [f.value_of_any_dependency(home_and_sds)
                            for f in self._fragments]
        return ''.join(fragment_strings)

    def __str__(self):
        return '{}([{}])'.format('StringValue',
                                 ','.join(map(str, self._fragments)))


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

    # def value_pre_sds(self, home_dir_path: pathlib.Path) -> str:
    #     return self.string_constant
    #
    # def value_post_sds(self, sds: SandboxDirectoryStructure) -> str:
    #     return self.string_constant

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
        return self.value.value_when_no_dir_dependencies()

    # def value_pre_sds(self, home_dir_path: pathlib.Path) -> str:
    #     return self._to_string(self.value.value_pre_sds(home_dir_path))
    #
    # def value_post_sds(self, sds: SandboxDirectoryStructure) -> str:
    #     return self._to_string(self.value.value_post_sds(sds))

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


class FileRefFragment(_StringFragmentFromDirDependentValue):
    def __init__(self, file_ref):
        super().__init__(file_ref)

    def _to_string(self, value) -> str:
        return str(value)

    def __str__(self):
        return '{}({})'.format('FileRefFragment',
                               repr(self.value))
