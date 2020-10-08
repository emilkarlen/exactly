import io
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import List, Sequence, ContextManager, Iterator, IO, Callable

from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatMustNoBeUsed
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources import test_of_test_resources_util
from exactly_lib_test.test_resources.actions import do_return, do_raise
from exactly_lib_test.type_system.logic.string_model.test_resources import assertions as sut
from exactly_lib_test.type_system.logic.string_model.test_resources import string_models


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestModelChecker)


class TestModelChecker(unittest.TestCase):
    put = test_of_test_resources_util.test_case_with_failure_exception_set_to_test_exception()

    def test_as_lines_should_accept_valid_model(self):
        # ARRANGE #
        cases = [
            NameAndValue(
                'empty list',
                [],
            ),
            NameAndValue(
                'single line, empty',
                [''],
            ),
            NameAndValue(
                'single line, not ended by nl',
                ['1'],
            ),
            NameAndValue(
                'single line, ended by nl',
                ['1\n'],
            ),
            NameAndValue(
                'single line, empty, ended by nl',
                ['\n'],
            ),
            NameAndValue(
                'multiple lines, empty',
                ['\n', ''],
            ),
            NameAndValue(
                'multiple lines, last not ended by nl',
                ['1\n', '2'],
            ),
            NameAndValue(
                'multiple line, last ended by nl',
                ['1\n', '2\n'],
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                model = self._model_with_checker(case.value)
                # ACT & ASSERT #
                output_lines = _get_all_lines(model)
                self.assertEqual(case.value,
                                 output_lines,
                                 'lines from checked model')

    def test_as_lines_should_detect_invalid_model(self):
        # ARRANGE #
        cases = [
            NameAndValue(
                'multiple new-lines at end, non-empty-line',
                ['1\n\n'],
            ),
            NameAndValue(
                'multiple new-lines at end, empty-line',
                ['\n\n'],
            ),
            NameAndValue(
                'new-line inside string, not ended by nl',
                ['a\nb'],
            ),
            NameAndValue(
                'new-line inside string, ended by nl',
                ['a\nb\n'],
            ),
            NameAndValue(
                'new-lines inside string',
                ['a\n\nb'],
            ),
            NameAndValue(
                'non-last line not ending with nl, last not ended by nl',
                ['1', '2'],
            ),
            NameAndValue(
                'non-last line not ending with nl, last ended by nl',
                ['1', '2\n'],
            ),
            NameAndValue(
                'multiple line, line in middle not ended by nl',
                ['1\n', '2', '3\n'],
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                model = self._model_with_checker(case.value)
                # ACT & ASSERT #
                with self.put.assertRaises(test_of_test_resources_util.TestException):
                    _get_all_lines(model)

    def test_tmp_file_space_should_call_wrapped_method(self):
        # ARRANGE #
        value_from_wrapped_method = DirFileSpaceThatMustNoBeUsed()

        wrapped_with_only_tmp_file_space_method = _StringModelThat(
            tmp_file_space=do_return(value_from_wrapped_method),
            as_str=do_raise(ValueError('should not be called')),
            as_file=do_raise(ValueError('should not be called')),
            write_to=do_raise(ValueError('should not be called')),
        )

        model = sut.StringModelThatThatChecksLines(self, wrapped_with_only_tmp_file_space_method)
        # ACT #
        actual = model._tmp_file_space
        # ASSERT #
        self.assertIs(actual, value_from_wrapped_method)

    def test_as_str_should_call_wrapped_method(self):
        # ARRANGE #
        value_from_wrapped_method = 'the str'

        wrapped_with_only_tmp_file_space_method = _StringModelThat(
            tmp_file_space=do_raise(ValueError('should not be called')),
            as_str=do_return(value_from_wrapped_method),
            as_file=do_raise(ValueError('should not be called')),
            write_to=do_raise(ValueError('should not be called')),
        )

        model = sut.StringModelThatThatChecksLines(self, wrapped_with_only_tmp_file_space_method)
        # ACT #
        actual = model.as_str
        # ASSERT #
        self.assertIs(actual, value_from_wrapped_method)

    def test_as_file_should_call_wrapped_method(self):
        # ARRANGE #
        value_from_wrapped_method = Path('the path')

        wrapped_with_only_tmp_file_space_method = _StringModelThat(
            tmp_file_space=do_raise(ValueError('should not be called')),
            as_str=do_raise(ValueError('should not be called')),
            as_file=do_return(value_from_wrapped_method),
            write_to=do_raise(ValueError('should not be called')),
        )

        model = sut.StringModelThatThatChecksLines(self, wrapped_with_only_tmp_file_space_method)
        # ACT #
        actual = model.as_file
        # ASSERT #
        self.assertIs(actual, value_from_wrapped_method)

    def test_write_to_should_call_wrapped_method(self):
        # ARRANGE #
        io_passed_to_wrapper = io.StringIO()

        def write_to_of_wrapped(f: IO):
            self.assertIs(f, io_passed_to_wrapper)

        wrapped_with_only_tmp_file_space_method = _StringModelThat(
            tmp_file_space=do_raise(ValueError('should not be called')),
            as_str=do_raise(ValueError('should not be called')),
            as_file=do_raise(ValueError('should not be called')),
            write_to=write_to_of_wrapped,
        )

        model = sut.StringModelThatThatChecksLines(self, wrapped_with_only_tmp_file_space_method)
        # ACT & ASSERT #
        model.write_to(io_passed_to_wrapper)

    def _model_with_checker(self, input_lines: Sequence[str]) -> sut.StringModelThatThatChecksLines:
        return sut.StringModelThatThatChecksLines(
            self.put,
            string_models.StringModelFromLines(
                input_lines,
                DirFileSpaceThatMustNoBeUsed(),
            )
        )


class _StringModelThat(StringModel):
    def __init__(self,
                 tmp_file_space: Callable[[], DirFileSpace],
                 as_str: Callable[[], str],
                 as_file: Callable[[], Path],
                 write_to: Callable[[IO], None],
                 ):
        self.__tmp_file_space = tmp_file_space
        self._as_str = as_str
        self._as_file = as_file
        self._write_to = write_to

    @property
    def _tmp_file_space(self) -> DirFileSpace:
        return self.__tmp_file_space()

    @property
    def as_str(self) -> str:
        return self._as_str()

    @property
    def as_file(self) -> Path:
        return self._as_file()

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        raise NotImplementedError('unsupported')

    def write_to(self, output: IO):
        self._write_to(output)


def _get_all_lines(model: sut.StringModelThatThatChecksLines) -> List[str]:
    with model.as_lines as lines:
        return list(lines)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
