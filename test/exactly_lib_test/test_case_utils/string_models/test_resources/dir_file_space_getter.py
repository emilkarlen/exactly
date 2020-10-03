import unittest
from contextlib import contextmanager
from typing import Callable, ContextManager

from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib_test.test_resources.files import tmp_dir
from exactly_lib_test.util.file_utils.test_resources.tmp_file_spaces import TmpFileSpaceThatAllowsSinglePathGeneration


def dir_file_space_for_single_usage_getter(put: unittest.TestCase) -> Callable[[], ContextManager[DirFileSpace]]:
    @contextmanager
    def ret_val() -> ContextManager[DirFileSpace]:
        with tmp_dir.tmp_dir() as storage_dir:
            yield TmpFileSpaceThatAllowsSinglePathGeneration(
                put,
                storage_dir,
                'path-name',
            )

    return ret_val
