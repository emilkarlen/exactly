import unittest
from contextlib import contextmanager
from typing import ContextManager, Sequence

from exactly_lib.type_val_deps.dep_variants.adv.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.string_model import StringModel
from exactly_lib_test.impls.types.string_model.test_resources.dir_file_space_getter import \
    dir_file_space_for_single_usage_getter
from exactly_lib_test.impls.types.string_model.test_resources.string_models import ModelFromLinesTestImpl
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_prims.string_model.test_resources import model_checker


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
        expectation = model_checker.Expectation.equals(
            ''.join(model_constructor.lines),
            may_depend_on_external_resources=asrt.anything_goes(),
        )

        checker = model_checker.Checker(
            self,
            model_constructor,
            expectation,
            dir_file_space_for_single_usage_getter(self),
        )
        # ACT & ASSERT #
        checker.check()


class _ModelConstructor(model_checker.ModelConstructor):
    def __init__(self, lines: Sequence[str]):
        self.lines = lines

    @contextmanager
    def new_with(self, app_env: ApplicationEnvironment) -> ContextManager[StringModel]:
        yield ModelFromLinesTestImpl(self.lines, app_env.tmp_files_space)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
