import unittest
from contextlib import contextmanager
from typing import ContextManager

from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatMustNoBeUsed
from exactly_lib_test.test_resources.files import tmp_dir
from exactly_lib_test.util.file_utils.test_resources import tmp_file_spaces
from exactly_lib_test.util.file_utils.test_resources.tmp_file_spaces import TmpFileSpaceThatAllowsSinglePathGeneration


@contextmanager
def dir_file_space_for_single_usage_getter(put: unittest.TestCase) -> ContextManager[DirFileSpace]:
    with tmp_dir.tmp_dir() as storage_dir:
        yield TmpFileSpaceThatAllowsSinglePathGeneration(
            put,
            storage_dir,
            'path-name',
        )


@contextmanager
def dir_file_space_that_must_not_be_used_getter(put: unittest.TestCase) -> ContextManager[DirFileSpace]:
    yield DirFileSpaceThatMustNoBeUsed()


@contextmanager
def dir_file_space_with_existing_dir() -> ContextManager[DirFileSpace]:
    with tmp_dir.tmp_dir() as storage_dir:
        yield tmp_file_spaces.tmp_dir_file_space_for_test(storage_dir)
