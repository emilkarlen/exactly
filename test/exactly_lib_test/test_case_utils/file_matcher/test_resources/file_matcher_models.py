import pathlib

from exactly_lib.test_case_utils.file_matcher.file_matcher_models import FileMatcherModelForPrimitivePath
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib_test.test_case_utils.err_msg.test_resources import described_path
from exactly_lib_test.util.test_resources.file_utils import TmpDirFileSpaceThatMustNoBeUsed


def with_dir_space_that_must_not_be_used(path: pathlib.Path) -> FileMatcherModel:
    return FileMatcherModelForPrimitivePath(TmpDirFileSpaceThatMustNoBeUsed(),
                                            described_path.new_primitive(path))
