import unittest
from contextlib import contextmanager
from typing import Iterator, Sequence, ContextManager

from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.impls import transformed_string_models as sut
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib_test.test_case_utils.string_models.test_resources.string_models import ModelFromLinesTestImpl
from exactly_lib_test.type_system.logic.string_model.test_resources import model_checker


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestTransformedStringModelFromLines(),
    ])


class TestTransformedStringModelFromLines(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        model_constructor = _ToUpperModelConstructor(
            _transformer_function,
            [
                '1st\n',
                '2nd\n',
            ]
        )
        expectation = model_checker.Expectation.equals(
            ''.join(_transformer_function(model_constructor.lines))
        )

        checker = model_checker.Checker(
            self,
            model_constructor,
            expectation,
        )
        # ACT & ASSERT #
        checker.check()


class _ToUpperModelConstructor(model_checker.ModelConstructor):
    def __init__(self,
                 transformation: sut.StringTransFun,
                 lines: Sequence[str],
                 ):
        self.transformation = transformation
        self.lines = lines

    @contextmanager
    def new_with(self, app_env: ApplicationEnvironment) -> ContextManager[StringModel]:
        source_model = ModelFromLinesTestImpl(
            self.lines,
            app_env.tmp_files_space,
        )

        yield sut.TransformedStringModelFromLines(
            self.transformation,
            source_model,
        )


def _transformer_function(lines: Iterator[str]) -> Iterator[str]:
    return map(str.upper, lines)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
