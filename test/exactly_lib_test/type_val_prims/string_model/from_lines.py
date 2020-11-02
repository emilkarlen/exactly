import unittest
from contextlib import contextmanager
from typing import Iterator, Sequence, ContextManager

from exactly_lib.type_val_deps.dep_variants.adv.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.impls import transformed_string_models as sut
from exactly_lib.type_val_prims.string_model import StringModel
from exactly_lib_test.impls.types.string_models.test_resources.string_models import ModelFromLinesTestImpl
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_prims.string_model.test_resources import model_checker


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestTransformedStringModelFromLines(),
    ])


class TestTransformedStringModelFromLines(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        for transformation_may_depend_on_external_resources in [False, True]:
            with self.subTest(transformation_may_depend_on_external_resources=
                              transformation_may_depend_on_external_resources):
                model_constructor = _ToUpperModelConstructor(
                    _transformer_function,
                    [
                        '1st\n',
                        '2nd\n',
                    ],
                    transformation_may_depend_on_external_resources,
                )
                expectation = model_checker.Expectation.equals(
                    ''.join(_transformer_function(model_constructor.lines)),
                    may_depend_on_external_resources=asrt.equals(transformation_may_depend_on_external_resources)
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
                 transformation_may_depend_on_external_resources: bool,
                 ):
        self.transformation = transformation
        self.lines = lines
        self.transformation_may_depend_on_external_resources = transformation_may_depend_on_external_resources

    @contextmanager
    def new_with(self, app_env: ApplicationEnvironment) -> ContextManager[StringModel]:
        source_model = ModelFromLinesTestImpl(
            self.lines,
            app_env.tmp_files_space,
        )

        yield sut.TransformedStringModelFromLines(
            self.transformation,
            source_model,
            self.transformation_may_depend_on_external_resources,
        )


def _transformer_function(lines: Iterator[str]) -> Iterator[str]:
    return map(str.upper, lines)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
