import io
import unittest
from pathlib import Path
from typing import List, Sequence, IO

from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatMustNoBeUsed
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources import test_of_test_resources_util
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.type_system.logic.string_model.test_resources import assertions as sut
from exactly_lib_test.type_system.logic.string_model.test_resources import string_models
from exactly_lib_test.type_system.logic.string_model.test_resources.string_models import StringModelThat


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

        wrapped = StringModelThat.new_w_defaults_of_not_impl(
            tmp_file_space=do_return(value_from_wrapped_method),
        )

        model = sut.StringModelThatThatChecksLines(self, wrapped)
        # ACT #
        actual = model._tmp_file_space
        # ASSERT #
        self.assertIs(actual, value_from_wrapped_method)

    def test_may_depend_on_external_resources_should_call_wrapped_method(self):
        # ARRANGE #
        for value_from_wrapped_method in [False, True]:
            with self.subTest(value_from_wrapped_method=value_from_wrapped_method):
                wrapped = StringModelThat.new_w_defaults_of_not_impl(
                    may_depend_on_external_resources=do_return(value_from_wrapped_method),
                )

                model = sut.StringModelThatThatChecksLines(self, wrapped)
                # ACT #
                actual = model.may_depend_on_external_resources
                # ASSERT #
                self.assertIs(actual, value_from_wrapped_method)

    def test_as_str_should_call_wrapped_method(self):
        # ARRANGE #
        value_from_wrapped_method = 'the str'

        wrapped = StringModelThat.new_w_defaults_of_not_impl(
            as_str=do_return(value_from_wrapped_method),
        )

        model = sut.StringModelThatThatChecksLines(self, wrapped)
        # ACT #
        actual = model.as_str
        # ASSERT #
        self.assertIs(actual, value_from_wrapped_method)

    def test_as_file_should_call_wrapped_method(self):
        # ARRANGE #
        value_from_wrapped_method = Path('the path')

        wrapped = StringModelThat.new_w_defaults_of_not_impl(
            as_file=do_return(value_from_wrapped_method),
        )

        model = sut.StringModelThatThatChecksLines(self, wrapped)
        # ACT #
        actual = model.as_file
        # ASSERT #
        self.assertIs(actual, value_from_wrapped_method)

    def test_write_to_should_call_wrapped_method(self):
        # ARRANGE #
        io_passed_to_wrapper = io.StringIO()

        def write_to_of_wrapped(f: IO):
            self.assertIs(f, io_passed_to_wrapper)

        wrapped = StringModelThat.new_w_defaults_of_not_impl(
            write_to=write_to_of_wrapped,
        )

        model = sut.StringModelThatThatChecksLines(self, wrapped)
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


def _get_all_lines(model: sut.StringModelThatThatChecksLines) -> List[str]:
    with model.as_lines as lines:
        return list(lines)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
