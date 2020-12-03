import unittest
from contextlib import contextmanager
from typing import Iterator, Sequence, IO, Callable, ContextManager

from exactly_lib.impls.types.string_transformer.impl.sources import transformed_string_sources as sut
from exactly_lib.type_val_deps.dep_variants.adv.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.impls.transformed_string_sources import StringTransFun
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.description_tree import renderers
from exactly_lib_test.impls.types.string_source.test_resources.string_sources import SourceFromLinesTestImpl
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_prims.string_source.test_resources import source_checker


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestTransformedByWriter),
    ])


class TestTransformedByWriter(unittest.TestCase):
    def test_arbitrary_model_method_invocations_in_arbitrary_order(self):
        # ARRANGE #
        source_constructor = _SourceConstructor(
            _transformer_function,
            [
                'a\n',
                'ab\n',
                '123\n',
            ]
        )
        expectation = source_checker.Expectation.equals(
            ''.join(_transformer_function(source_constructor.raw_lines)),
            may_depend_on_external_resources=asrt.equals(True),
        )

        checker = source_checker.Checker(
            self,
            source_constructor,
            expectation,
        )
        # ACT & ASSERT #
        checker.check()

    def test_writer_SHOULD_not_be_invoked_after_file_path_has_been_requested(self):
        # ARRANGE #
        source_constructor = _SourceConstructorWithWriterThatMustBeAppliedOnlyOnce(
            self,
            _transformer_function,
            [
                'a\n',
                'ab\n',
                '123\n',
            ]
        )
        expectation = source_checker.Expectation.equals(
            ''.join(_transformer_function(source_constructor.raw_lines)),
            may_depend_on_external_resources=asrt.equals(True),
        )

        checker = source_checker.Checker(
            self,
            source_constructor,
            expectation,
        )
        # ACT & ASSERT #
        checker.check_with_first_access_is_not_write_to()


class _SourceConstructor(source_checker.SourceConstructor):
    def __init__(self,
                 transformation: StringTransFun,
                 raw_lines: Sequence[str],
                 ):
        self.transformation = transformation
        self.raw_lines = raw_lines

    @contextmanager
    def new_with(self, app_env: ApplicationEnvironment) -> ContextManager[StringSource]:
        source_model = SourceFromLinesTestImpl(
            self.raw_lines,
            app_env.tmp_files_space,
        )

        yield sut.TransformedStringSourceFromWriter(
            _TransformAndWriteToFile(app_env, self.transformation).write,
            source_model,
            _get_transformer_structure,
        )


class _SourceConstructorWithWriterThatMustBeAppliedOnlyOnce(source_checker.SourceConstructor):
    def __init__(self,
                 put: unittest.TestCase,
                 transformation: StringTransFun,
                 raw_lines: Sequence[str],
                 ):
        self.put = put
        self.transformation = transformation
        self.raw_lines = raw_lines

    @contextmanager
    def new_with(self, app_env: ApplicationEnvironment) -> ContextManager[StringSource]:
        source_model = SourceFromLinesTestImpl(
            self.raw_lines,
            app_env.tmp_files_space,
        )

        yield sut.TransformedStringSourceFromWriter(
            _TransformAndWriteToFileThatMustBeInvokedOnlyOnce(
                self.put,
                _TransformAndWriteToFile(app_env, self.transformation).write
            ).write,
            source_model,
            _get_transformer_structure,
        )


class _TransformAndWriteToFile:
    def __init__(self,
                 app_env: ApplicationEnvironment,
                 transformer_function: StringTransFun,
                 ):
        self._app_env = app_env
        self._transformer_function = transformer_function

    def write(self, source: StringSource, output: IO) -> None:
        with source.as_lines as lines:
            output.writelines(
                self._transformer_function(lines)
            )


class _TransformAndWriteToFileThatMustBeInvokedOnlyOnce:
    def __init__(self,
                 put: unittest.TestCase,
                 writer: Callable[[StringSource, IO], None],
                 ):
        self._put = put
        self._writer = writer
        self._num_invocations = 0

    def write(self, source: StringSource, output: IO) -> None:
        self._put.assertEqual(0, self._num_invocations)
        self._num_invocations += 1

        self._writer(source, output)


def _transformer_function(lines: Iterator[str]) -> Iterator[str]:
    return map(str.upper, lines)


def _get_transformer_structure() -> StructureRenderer:
    return renderers.header_only('the-transformer')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
