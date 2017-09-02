import pathlib

from exactly_lib.test_case_file_structure.dir_dependent_value import SingleDirDependentValue
from exactly_lib.test_case_file_structure.home_directory_structure import HomeDirectoryStructure
from exactly_lib.test_case_file_structure.path_relativity import SpecificPathRelativity, RESOLVING_DEPENDENCY_OF, \
    ResolvingDependency
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.type_system.data.path_part import PathPart


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

    def value_pre_sds(self, hds: HomeDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def value_post_sds(self, sds: SandboxDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()
