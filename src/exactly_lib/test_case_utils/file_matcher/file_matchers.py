import os
from typing import Iterator

from exactly_lib.test_case_utils.file_matcher.file_matcher_models import FileMatcherModelForDescribedPath
from exactly_lib.test_case_utils.matcher.impls import constant
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.file_matcher import FileMatcher

MATCH_EVERY_FILE = constant.MatcherWithConstantResult(True)


def matching_files_in_dir(matcher: FileMatcher,
                          dir_path: DescribedPath) -> Iterator[str]:
    return (
        file_name
        for file_name in os.listdir(str(dir_path.primitive))
        if matcher.matches_w_trace(FileMatcherModelForDescribedPath(dir_path.child(file_name))).value
    )
