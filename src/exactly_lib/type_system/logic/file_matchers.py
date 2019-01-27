import pathlib
from typing import Iterator, Set

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherValue


def matching_files_in_dir(matcher: FileMatcher, dir_path: pathlib.Path) -> Iterator[pathlib.Path]:
    return filter(matcher.matches, dir_path.iterdir())


class FileMatcherValueFromPrimitiveValue(FileMatcherValue):
    def __init__(self, primitive_value: FileMatcher):
        self._primitive_value = primitive_value

    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return set()

    def value_when_no_dir_dependencies(self) -> FileMatcher:
        return self._primitive_value

    def value_of_any_dependency(self, tcds: HomeAndSds) -> FileMatcher:
        return self._primitive_value
