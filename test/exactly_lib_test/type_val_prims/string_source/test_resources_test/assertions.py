import io
import unittest
from pathlib import Path
from typing import List, Sequence, TextIO

from exactly_lib.util.file_utils.dir_file_spaces import DirFileSpaceThatMustNoBeUsed
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.test_resources import test_of_test_resources_util
from exactly_lib_test.test_resources.actions import do_return
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as sut, string_sources, \
    string_source_contents
from exactly_lib_test.type_val_prims.string_source.test_resources.string_sources import StringSourceOfContents


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

        wrapped = StringSourceOfContents.of_identical(
            string_source_contents.StringSourceContentsThat.new_w_defaults_of_not_impl(
                tmp_file_space=do_return(value_from_wrapped_method),
            )
        )

        source = sut.StringSourceThatThatChecksLines(self, wrapped)
        # ACT #
        actual = source.contents().tmp_file_space
        # ASSERT #
        self.assertIs(actual, value_from_wrapped_method)

    def test_may_depend_on_external_resources_should_call_wrapped_method(self):
        # ARRANGE #
        for value_from_wrapped_method in [False, True]:
            with self.subTest(value_from_wrapped_method=value_from_wrapped_method):
                wrapped = StringSourceOfContents.of_identical(
                    string_source_contents.StringSourceContentsThat.new_w_defaults_of_not_impl(
                        may_depend_on_external_resources=do_return(value_from_wrapped_method),
                    )
                )

                source = sut.StringSourceThatThatChecksLines(self, wrapped)
                # ACT #
                actual = source.contents().may_depend_on_external_resources
                # ASSERT #
                self.assertIs(actual, value_from_wrapped_method)

    def test_as_str_should_call_wrapped_method(self):
        # ARRANGE #
        value_from_wrapped_method = 'the str'
        wrapped = StringSourceOfContents.of_identical(
            string_source_contents.StringSourceContentsThat.new_w_defaults_of_not_impl(
                as_str=do_return(value_from_wrapped_method),
            )
        )

        source = sut.StringSourceThatThatChecksLines(self, wrapped)
        # ACT #
        actual = source.contents().as_str
        # ASSERT #
        self.assertIs(actual, value_from_wrapped_method)

    def test_as_file_should_call_wrapped_method(self):
        # ARRANGE #
        value_from_wrapped_method = Path('the path')

        wrapped = StringSourceOfContents.of_identical(
            string_source_contents.StringSourceContentsThat.new_w_defaults_of_not_impl(
                as_file=do_return(value_from_wrapped_method),
            )
        )

        source = sut.StringSourceThatThatChecksLines(self, wrapped)
        # ACT #
        actual = source.contents().as_file
        # ASSERT #
        self.assertIs(actual, value_from_wrapped_method)

    def test_write_to_should_call_wrapped_method(self):
        # ARRANGE #
        io_passed_to_wrapper = io.StringIO()

        def write_to_of_wrapped(f: TextIO):
            self.assertIs(f, io_passed_to_wrapper)

        wrapped = StringSourceOfContents.of_identical(
            string_source_contents.StringSourceContentsThat.new_w_defaults_of_not_impl(
                write_to=write_to_of_wrapped,
            )
        )

        source = sut.StringSourceThatThatChecksLines(self, wrapped)
        # ACT & ASSERT #
        source.contents().write_to(io_passed_to_wrapper)

    def _model_with_checker(self, input_lines: Sequence[str]) -> sut.StringSourceThatThatChecksLines:
        return sut.StringSourceThatThatChecksLines(
            self.put,
            string_sources.string_source_from_lines(
                input_lines,
                DirFileSpaceThatMustNoBeUsed(),
            )
        )


def _get_all_lines(model: sut.StringSourceThatThatChecksLines) -> List[str]:
    with model.contents().as_lines as lines:
        return list(lines)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
