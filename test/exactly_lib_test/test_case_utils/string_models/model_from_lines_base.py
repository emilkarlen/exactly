import unittest
from contextlib import contextmanager
from typing import ContextManager, Sequence, Callable

from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib_test.test_case_utils.string_models.test_resources.string_models import ModelFromLinesTestImpl
from exactly_lib_test.test_resources.files import tmp_dir
from exactly_lib_test.type_system.logic.string_model.test_resources import model_checker
from exactly_lib_test.util.file_utils.test_resources.tmp_file_spaces import TmpFileSpaceThatAllowsSinglePathGeneration


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestModelFromLinesBase(),
    ])


class TestModelFromLinesBase(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        model_constructor = _ModelConstructor([
            '1st\n',
            '2nd\n',
        ]
        )
        expectation = model_checker.Expectation.equals(''.join(model_constructor.lines))

        checker = model_checker.Checker(
            self,
            model_constructor,
            expectation,
            _dir_file_space_for_single_usage_getter(self),
        )
        # ACT & ASSERT #
        checker.check()


def _dir_file_space_for_single_usage_getter(put: unittest.TestCase) -> Callable[[], ContextManager[DirFileSpace]]:
    @contextmanager
    def ret_val() -> ContextManager[DirFileSpace]:
        with tmp_dir.tmp_dir() as storage_dir:
            yield TmpFileSpaceThatAllowsSinglePathGeneration(
                put,
                storage_dir,
                'path-name',
            )

    return ret_val


class _ModelConstructor(model_checker.ModelConstructor):
    def __init__(self, lines: Sequence[str]):
        self.lines = lines

    @contextmanager
    def new_with(self, app_env: ApplicationEnvironment) -> ContextManager[StringModel]:
        yield ModelFromLinesTestImpl(self.lines, app_env.tmp_files_space)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
