import unittest
from contextlib import contextmanager
from typing import Iterator, Sequence, ContextManager

from exactly_lib.type_val_deps.dep_variants.adv.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.impls import transformed_string_sources as sut
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.description_tree import renderers
from exactly_lib_test.impls.types.string_source.test_resources.string_sources import SourceFromLinesTestImpl
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_prims.string_source.test_resources import source_checker


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestTransformedStringSourceFromLines(),
    ])


class TestTransformedStringSourceFromLines(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        for transformation_may_depend_on_external_resources in [False, True]:
            with self.subTest(transformation_may_depend_on_external_resources=
                              transformation_may_depend_on_external_resources):
                source_constructor = _ToUpperSourceConstructor(
                    _transformer_function,
                    [
                        '1st\n',
                        '2nd\n',
                    ],
                    transformation_may_depend_on_external_resources,
                )
                expectation = source_checker.Expectation.equals(
                    ''.join(_transformer_function(source_constructor.lines)),
                    may_depend_on_external_resources=asrt.equals(transformation_may_depend_on_external_resources)
                )

                checker = source_checker.Checker(
                    self,
                    source_constructor,
                    expectation,
                )
                # ACT & ASSERT #
                checker.check()


class _ToUpperSourceConstructor(source_checker.SourceConstructor):
    def __init__(self,
                 transformation: sut.StringTransFun,
                 lines: Sequence[str],
                 transformation_may_depend_on_external_resources: bool,
                 ):
        self.transformation = transformation
        self.lines = lines
        self.transformation_may_depend_on_external_resources = transformation_may_depend_on_external_resources

    @contextmanager
    def new_with(self, app_env: ApplicationEnvironment) -> ContextManager[StringSource]:
        source_model = SourceFromLinesTestImpl(
            self.lines,
            app_env.tmp_files_space,
        )

        yield sut.TransformedStringSourceFromLines(
            self.transformation,
            source_model,
            self.transformation_may_depend_on_external_resources,
            _get_transformer_structure,
        )


def _get_transformer_structure() -> StructureRenderer:
    return renderers.header_only('the-transformer')


def _transformer_function(lines: Iterator[str]) -> Iterator[str]:
    return map(str.upper, lines)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
