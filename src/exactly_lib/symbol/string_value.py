import pathlib

from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


class StringWithDirDependency(DirDependentValue):
    def value_pre_sds(self, home_dir_path: pathlib.Path) -> str:
        raise NotImplementedError()

    def value_post_sds(self, sds: SandboxDirectoryStructure) -> str:
        raise NotImplementedError()

    def value_pre_or_post_sds(self, home_and_sds: HomeAndSds) -> str:
        if self.exists_pre_sds():
            return self.value_pre_sds(home_and_sds.home_dir_path)
        else:
            return self.value_post_sds(home_and_sds.sds)


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

    def has_dir_dependency(self) -> bool:
        return any([fragment.has_dir_dependency()
                    for fragment in self._fragments])

    def exists_pre_sds(self) -> bool:
        return all([fragment.exists_pre_sds()
                    for fragment in self._fragments])

    def value_when_no_dir_dependencies(self):
        fragment_strings = [f.value_when_no_dir_dependencies()
                            for f in self._fragments]
        return ''.join(fragment_strings)

    def value_pre_sds(self, home_dir_path: pathlib.Path) -> str:
        fragment_strings = [f.value_pre_sds(home_dir_path)
                            for f in self._fragments]
        return ''.join(fragment_strings)

    def value_post_sds(self, sds: SandboxDirectoryStructure) -> str:
        fragment_strings = [f.value_post_sds(sds)
                            for f in self._fragments]
        return ''.join(fragment_strings)

    def value_pre_or_post_sds(self, home_and_sds: HomeAndSds) -> str:
        fragment_strings = [f.value_pre_or_post_sds(home_and_sds)
                            for f in self._fragments]
        return ''.join(fragment_strings)


class ConstantFragment(StringFragment):
    def __init__(self, string_constant: str):
        self.string_constant = string_constant

    def has_dir_dependency(self) -> bool:
        return False

    def exists_pre_sds(self) -> bool:
        return True

    def value_when_no_dir_dependencies(self):
        return self.string_constant

    def value_pre_sds(self, home_dir_path: pathlib.Path) -> str:
        return self.string_constant

    def value_post_sds(self, sds: SandboxDirectoryStructure) -> str:
        return self.string_constant

    def value_pre_or_post_sds(self, home_and_sds: HomeAndSds) -> str:
        return self.string_constant


class FileRefFragment(StringFragment):
    def __init__(self, file_ref):
        self.file_ref = file_ref

    def has_dir_dependency(self) -> bool:
        return self.file_ref.has_dir_dependency()

    def exists_pre_sds(self) -> bool:
        return self.file_ref.exists_pre_sds()

    def value_when_no_dir_dependencies(self):
        return self.file_ref.value_when_no_dir_dependencies()

    def value_pre_sds(self, home_dir_path: pathlib.Path) -> str:
        return str(self.file_ref.value_pre_sds())

    def value_post_sds(self, sds: SandboxDirectoryStructure) -> str:
        return str(self.file_ref.value_post_sds())

    def value_pre_or_post_sds(self, home_and_sds: HomeAndSds) -> str:
        return str(self.file_ref.value_pre_or_post_sds())
