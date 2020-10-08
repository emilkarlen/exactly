import unittest
from contextlib import contextmanager
from typing import Iterator, Sequence, IO, Callable, ContextManager

from exactly_lib.test_case_utils.string_transformer.impl.models import transformed_string_models as sut
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.impls.transformed_string_models import StringTransFun
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib_test.test_case_utils.string_models.test_resources.string_models import ModelFromLinesTestImpl
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_model.test_resources import model_checker


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestTransformedByWriter),
    ])


class TestTransformedByWriter(unittest.TestCase):
    def test_arbitrary_model_method_invocations_in_arbitrary_order(self):
        # ARRANGE #
        model_constructor = _ModelConstructor(
            _transformer_function,
            [
                'a\n',
                'ab\n',
                '123\n',
            ]
        )
        expectation = model_checker.Expectation.equals(
            ''.join(_transformer_function(model_constructor.raw_lines)),
            may_depend_on_external_resources=asrt.equals(True),
        )

        checker = model_checker.Checker(
            self,
            model_constructor,
            expectation,
        )
        # ACT & ASSERT #
        checker.check()

    def test_writer_SHOULD_not_be_invoked_after_file_path_has_been_requested(self):
        # ARRANGE #
        model_constructor = _ModelConstructorWithWriterThatMustBeAppliedOnlyOnce(
            self,
            _transformer_function,
            [
                'a\n',
                'ab\n',
                '123\n',
            ]
        )
        expectation = model_checker.Expectation.equals(
            ''.join(_transformer_function(model_constructor.raw_lines)),
            may_depend_on_external_resources=asrt.equals(True),
        )

        checker = model_checker.Checker(
            self,
            model_constructor,
            expectation,
        )
        # ACT & ASSERT #
        checker.check_with_first_access_is_not_write_to()


class _ModelConstructor(model_checker.ModelConstructor):
    def __init__(self,
                 transformation: StringTransFun,
                 raw_lines: Sequence[str],
                 ):
        self.transformation = transformation
        self.raw_lines = raw_lines

    @contextmanager
    def new_with(self, app_env: ApplicationEnvironment) -> ContextManager[StringModel]:
        source_model = ModelFromLinesTestImpl(
            self.raw_lines,
            app_env.tmp_files_space,
        )

        yield sut.TransformedStringModelFromWriter(
            _TransformAndWriteToFile(app_env, self.transformation).write,
            source_model,
        )


class _ModelConstructorWithWriterThatMustBeAppliedOnlyOnce(model_checker.ModelConstructor):
    def __init__(self,
                 put: unittest.TestCase,
                 transformation: StringTransFun,
                 raw_lines: Sequence[str],
                 ):
        self.put = put
        self.transformation = transformation
        self.raw_lines = raw_lines

    @contextmanager
    def new_with(self, app_env: ApplicationEnvironment) -> ContextManager[StringModel]:
        source_model = ModelFromLinesTestImpl(
            self.raw_lines,
            app_env.tmp_files_space,
        )

        yield sut.TransformedStringModelFromWriter(
            _TransformAndWriteToFileThatMustBeInvokedOnlyOnce(
                self.put,
                _TransformAndWriteToFile(app_env, self.transformation).write
            ).write,
            source_model,
        )


class _TransformAndWriteToFile:
    def __init__(self,
                 app_env: ApplicationEnvironment,
                 transformer_function: StringTransFun,
                 ):
        self._app_env = app_env
        self._transformer_function = transformer_function

    def write(self, source: StringModel, output: IO) -> None:
        with source.as_lines as lines:
            output.writelines(
                self._transformer_function(lines)
            )


class _TransformAndWriteToFileThatMustBeInvokedOnlyOnce:
    def __init__(self,
                 put: unittest.TestCase,
                 writer: Callable[[StringModel, IO], None],
                 ):
        self._put = put
        self._writer = writer
        self._num_invocations = 0

    def write(self, source: StringModel, output: IO) -> None:
        self._put.assertEqual(0, self._num_invocations)
        self._num_invocations += 1

        self._writer(source, output)


def _transformer_function(lines: Iterator[str]) -> Iterator[str]:
    return map(str.upper, lines)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
