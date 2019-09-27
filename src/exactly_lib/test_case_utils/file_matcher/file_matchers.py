import os
from typing import Iterator

from exactly_lib.test_case_utils.file_matcher.file_matcher_models import FileMatcherModelForPrimitivePath
from exactly_lib.test_case_utils.file_matcher.impl.impl_base_class import FileMatcherImplBase
from exactly_lib.type_system.data.described_path import DescribedPathPrimitive
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatchingResult
from exactly_lib.util.file_utils import TmpDirFileSpace


class FileMatcherConstant(FileMatcherImplBase):
    """Selects files from a directory according the a file condition."""

    def __init__(self, result: bool):
        self._result = result

    @property
    def result_constant(self) -> bool:
        return self._result

    @property
    def name(self) -> str:
        return self.option_description

    @property
    def option_description(self) -> str:
        return 'any file' if self._result else 'no file'

    @property
    def negation(self) -> FileMatcher:
        return FileMatcherConstant(not self._result)

    def matches(self, model: FileMatcherModel) -> bool:
        return self._result

    def matches_w_trace(self, model: FileMatcherModel) -> MatchingResult:
        return self._new_tb().build_result(self._result)


MATCH_EVERY_FILE = FileMatcherConstant(True)


def matching_files_in_dir(matcher: FileMatcher,
                          tmp_file_space: TmpDirFileSpace,
                          dir_path: DescribedPathPrimitive) -> Iterator[str]:
    return (
        file_name
        for file_name in os.listdir(str(dir_path.primitive))
        if matcher.matches(FileMatcherModelForPrimitivePath(tmp_file_space,
                                                            dir_path.child(file_name)))
    )
