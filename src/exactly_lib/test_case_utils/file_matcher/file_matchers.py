import os
from typing import Iterator

from exactly_lib.test_case_utils.file_matcher.file_matcher_models import FileMatcherModelForPrimitivePath
from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib.type_system.data.path_ddv import DescribedPathPrimitive
from exactly_lib.type_system.logic.file_matcher import FileMatcher
from exactly_lib.util.file_utils import TmpDirFileSpace

MATCH_EVERY_FILE = constant.MatcherWithConstantResult(True)


def matching_files_in_dir(matcher: FileMatcher,
                          tmp_file_space: TmpDirFileSpace,
                          dir_path: DescribedPathPrimitive) -> Iterator[str]:
    return (
        file_name
        for file_name in os.listdir(str(dir_path.primitive))
        if matcher.matches(FileMatcherModelForPrimitivePath(tmp_file_space,
                                                            dir_path.child(file_name)))
    )
