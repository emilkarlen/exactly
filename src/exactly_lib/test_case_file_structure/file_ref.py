import pathlib

from exactly_lib.test_case_file_structure.dir_dependent_value import SingleDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_part import PathPart
from exactly_lib.test_case_file_structure.path_relativity import SpecificPathRelativity, RESOLVING_DEPENDENCY_OF, \
    ResolvingDependency
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure


class FileRef(SingleDirDependentValue):
    """
    A reference to a file (any kind of file), with functionality to resolve it's path,
    and information about whether it exists pre SDS or not.
    """

    def path_suffix(self) -> PathPart:
        raise NotImplementedError()

    def path_suffix_str(self) -> str:
        raise NotImplementedError()

    def path_suffix_path(self) -> pathlib.Path:
        raise NotImplementedError()

    def exists_pre_sds(self) -> bool:
        return self.resolving_dependency() is not ResolvingDependency.NON_HOME

    def resolving_dependency(self) -> ResolvingDependency:
        relativity = self.relativity()
        if relativity.is_absolute:
            return None
        else:
            return RESOLVING_DEPENDENCY_OF[relativity.relativity_type]

    def resolving_dependencies(self) -> set:
        relativity = self.relativity()
        if relativity.is_absolute:
            return set()
        else:
            return {RESOLVING_DEPENDENCY_OF[relativity.relativity_type]}

    def relativity(self) -> SpecificPathRelativity:
        raise NotImplementedError()

    def value_when_no_dir_dependencies(self) -> pathlib.Path:
        raise NotImplementedError()

    def value_pre_sds(self, home_dir_path: pathlib.Path) -> pathlib.Path:
        raise NotImplementedError()

    def value_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def value_pre_or_post_sds(self, home_and_sds: HomeAndSds) -> pathlib.Path:
        if self.exists_pre_sds():
            return self.value_pre_sds(home_and_sds.home_dir_path)
        else:
            return self.value_post_sds(home_and_sds.sds)
