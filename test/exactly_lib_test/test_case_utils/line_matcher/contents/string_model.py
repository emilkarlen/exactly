import unittest
from contextlib import contextmanager
from typing import ContextManager

from exactly_lib.test_case_utils.line_matcher.impl.contents import string_model as sut
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib_test.test_case_utils.string_models.test_resources.dir_file_space_getter import \
    dir_file_space_for_single_usage_getter
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_model.test_resources import model_checker


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestStringModel(),
    ])


class TestStringModel(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        model_constructor = _ModelConstructor('the contents of the line')
        expectation = model_checker.Expectation.equals(
            model_constructor.contents,
            may_depend_on_external_resources=asrt.equals(False),
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
    def __init__(self, contents: str):
        self.contents = contents

    @contextmanager
    def new_with(self, app_env: ApplicationEnvironment) -> ContextManager[StringModel]:
        yield sut.StringModel(
            self.contents,
            app_env.tmp_files_space,
        )