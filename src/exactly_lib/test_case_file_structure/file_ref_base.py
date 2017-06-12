import pathlib

from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependencyError
from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.path_part import PathPart
from exactly_lib.test_case_file_structure.path_relativity import SpecificPathRelativity, specific_relative_relativity, \
    RelOptionType, DIR_DEPENDENCY_OF


class FileRefWithPathSuffixBase(FileRef):
    def __init__(self, path_part: PathPart):
        self._path_suffix = path_part

    def path_suffix(self) -> PathPart:
        return self._path_suffix

    def path_suffix_str(self) -> str:
        return self._path_suffix.resolve()

    def path_suffix_path(self) -> pathlib.Path:
        return pathlib.Path(self.path_suffix_str())


class FileRefWithPathSuffixAndIsNotAbsoluteBase(FileRefWithPathSuffixBase):
    def __init__(self, path_part: PathPart):
        super().__init__(path_part)

    def has_dir_dependency(self) -> bool:
        return True

    def value_when_no_dir_dependencies(self) -> pathlib.Path:
        raise DirDependencyError(DIR_DEPENDENCY_OF[self._relativity()])

    def relativity(self) -> SpecificPathRelativity:
        rel_option_type = self._relativity()
        return specific_relative_relativity(rel_option_type)

    def _relativity(self) -> RelOptionType:
        raise NotImplementedError()
