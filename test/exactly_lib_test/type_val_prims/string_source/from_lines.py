import unittest
from contextlib import contextmanager
from typing import Iterator, Sequence, ContextManager

from exactly_lib.type_val_deps.dep_variants.adv.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.string_source.impls import transformed_string_sources as sut
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.description_tree import renderers
from exactly_lib_test.impls.types.string_source.test_resources.string_sources import source_from_lines_test_impl
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_val_prims.string_source.test_resources import multi_obj_assertions
from exactly_lib_test.type_val_prims.string_source.test_resources.source_constructors import \
    SourceConstructorWAppEnvForTest


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
                source_constructor = _SourceConstructorOfTransFun(
                    _transformer_function,
                    [
                        '1st\n',
                        '2nd\n',
                    ],
                    transformation_may_depend_on_external_resources,
                )
                expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
                    ''.join(_transformer_function(source_constructor.lines)),
                    may_depend_on_external_resources=
                    asrt.equals(transformation_may_depend_on_external_resources),
                    frozen_may_depend_on_external_resources=
                    asrt.equals(transformation_may_depend_on_external_resources),
                )

                assertion = multi_obj_assertions.assertion_of_sequence_permutations(expectation)
                # ACT & ASSERT #
                assertion.apply_without_message(
                    self,
                    multi_obj_assertions.SourceConstructors.of_common(source_constructor),
                )


class _SourceConstructorOfTransFun(SourceConstructorWAppEnvForTest):
    def __init__(self,
                 transformation: sut.StringTransFun,
                 lines: Sequence[str],
                 transformation_may_depend_on_external_resources: bool,
                 ):
        super().__init__()
        self.transformation = transformation
        self.lines = lines
        self.transformation_may_depend_on_external_resources = transformation_may_depend_on_external_resources

    @contextmanager
    def new_with(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder,
                 app_env: ApplicationEnvironment,
                 ) -> ContextManager[StringSource]:
        source_model = source_from_lines_test_impl(
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
