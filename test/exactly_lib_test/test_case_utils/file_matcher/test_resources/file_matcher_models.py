import pathlib

from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib_test.util.test_resources.file_utils import TmpDirFileSpaceThatMustNoBeUsed


def with_tmp_dir_space_that_must_not_be_used(path: pathlib.Path) -> FileMatcherModel:
    return FileMatcherModel(TmpDirFileSpaceThatMustNoBeUsed(),
                            path)
