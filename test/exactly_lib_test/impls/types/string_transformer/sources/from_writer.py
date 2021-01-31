import unittest
from contextlib import contextmanager
from typing import Iterator, Sequence, Callable, ContextManager, TextIO

from exactly_lib.impls.types.string_transformer.impl.sources import transformed_string_sources as sut
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.type_val_prims.string_source.impls.transformed_string_sources import StringTransFun
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.description_tree import renderers
from exactly_lib_test.impls.types.string_source.test_resources.string_sources import source_from_lines_test_impl
from exactly_lib_test.test_resources.recording import MaxNumberOfTimesChecker
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_val_prims.string_source.test_resources import multi_obj_assertions
from exactly_lib_test.type_val_prims.string_source.test_resources.source_constructors import \
    SourceConstructorWAppEnvForTest


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
        expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
            ''.join(_transformer_function(source_constructor.raw_lines)),
            may_depend_on_external_resources=asrt.equals(True),
            frozen_may_depend_on_external_resources=asrt.anything_goes(),
        )

        assertion = multi_obj_assertions.assertion_of_sequence_permutations(expectation)
        # ACT & ASSERT #
        assertion.apply_without_message(
            self,
            multi_obj_assertions.SourceConstructors.of_common(source_constructor),
        )

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
        expectation = multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
            ''.join(_transformer_function(source_constructor.raw_lines)),
            may_depend_on_external_resources=asrt.equals(True),
            frozen_may_depend_on_external_resources=asrt.anything_goes(),
        )

        assertion = multi_obj_assertions.assertion_of_first_access_is_not_write_to(expectation)
        # ACT & ASSERT #
        assertion.apply_without_message(
            self,
            multi_obj_assertions.SourceConstructors.of_common(source_constructor),
        )


class _SourceConstructor(SourceConstructorWAppEnvForTest):
    def __init__(self,
                 transformation: StringTransFun,
                 raw_lines: Sequence[str],
                 ):
        super().__init__()
        self.transformation = transformation
        self.raw_lines = raw_lines

    @contextmanager
    def new_with(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder,
                 app_env: ApplicationEnvironment,
                 ) -> ContextManager[StringSource]:
        source_model = source_from_lines_test_impl(
            self.raw_lines,
            app_env.tmp_files_space,
        )

        yield sut.transformed_string_source_from_writer(
            _TransformAndWriteToFile(app_env, self.transformation).write,
            source_model,
            _get_transformer_structure,
            app_env.mem_buff_size,
        )


class _SourceConstructorWithWriterThatMustBeAppliedOnlyOnce(SourceConstructorWAppEnvForTest):
    def __init__(self,
                 put: unittest.TestCase,
                 transformation: StringTransFun,
                 raw_lines: Sequence[str],
                 ):
        super().__init__()
        self.put = put
        self.transformation = transformation
        self.raw_lines = raw_lines

    @contextmanager
    def new_with(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder,
                 app_env: ApplicationEnvironment,
                 ) -> ContextManager[StringSource]:
        source_model = source_from_lines_test_impl(
            self.raw_lines,
            app_env.tmp_files_space,
        )

        yield sut.transformed_string_source_from_writer(
            _TransformAndWriteToFileThatMustBeInvokedOnlyOnce(
                self.put,
                _TransformAndWriteToFile(app_env, self.transformation).write,
                message_builder,
            ).write,
            source_model,
            _get_transformer_structure,
            app_env.mem_buff_size,
        )


class _TransformAndWriteToFile:
    def __init__(self,
                 app_env: ApplicationEnvironment,
                 transformer_function: StringTransFun,
                 ):
        self._app_env = app_env
        self._transformer_function = transformer_function

    def write(self, source: StringSourceContents, output: TextIO) -> None:
        with source.as_lines as lines:
            output.writelines(
                self._transformer_function(lines)
            )


class _TransformAndWriteToFileThatMustBeInvokedOnlyOnce:
    def __init__(self,
                 put: unittest.TestCase,
                 writer: Callable[[StringSourceContents, TextIO], None],
                 message_builder: asrt.MessageBuilder,
                 ):
        self._put = put
        self._writer = writer
        self._max_num_invocations_counter = MaxNumberOfTimesChecker(put, 1, 'transform-and-write',
                                                                    message_builder.apply(''))

    def write(self, source: StringSourceContents, output: TextIO) -> None:
        self._max_num_invocations_counter.register()
        self._writer(source, output)


def _transformer_function(lines: Iterator[str]) -> Iterator[str]:
    return map(str.upper, lines)


def _get_transformer_structure() -> StructureRenderer:
    return renderers.header_only('the-transformer')


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
