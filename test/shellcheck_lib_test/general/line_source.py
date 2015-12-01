import os
import unittest

from shellcheck_lib.general import line_source
from shellcheck_lib_test.util.file_utils import tmp_file_containing


def line(line_number: int, text: str) -> line_source.Line:
    return line_source.Line(line_number, text)


class TestStringLineSource(unittest.TestCase):
    def test_empty_string_should_be_no_lines(self):
        line_source_for_empty_string = line_source.new_for_string('')
        actual = tuple(iter(line_source_for_empty_string))
        self.assertEqual((), actual)

    def test_non_empty_without_linesep_should_give_single_line(self):
        line_source_for_single_line = line_source.new_for_string('single line')
        actual = list(iter(line_source_for_single_line))
        expected = [line(1, 'single line')]
        self.assertEqual(expected, actual)

    def test_single_linesep_should_give_two_lines(self):
        two_lines = os.linesep.join(['first', 'second'])
        line_source_for_two_lines = line_source.new_for_string(two_lines)
        actual = list(iter(line_source_for_two_lines))
        expected = [line(1, 'first'), line(2, 'second')]
        self.assertEqual(expected, actual)

    def test_trailing_linesep_should_produce_no_line(self):
        single_line_with_linesep = 'first' + os.linesep
        line_source_for_two_lines = line_source.new_for_string(single_line_with_linesep)
        actual = list(iter(line_source_for_two_lines))
        expected = [line(1, 'first')]
        self.assertEqual(expected, actual)

    def test_empty_line(self):
        contents = 'first' + os.linesep + os.linesep
        line_source_for_two_lines = line_source.new_for_string(contents)
        actual = list(iter(line_source_for_two_lines))
        expected = [line(1, 'first'),
                    line(2, '')]
        self.assertEqual(expected, actual)


class TestFileLineSource(unittest.TestCase):
    def test_empty_string_should_be_no_lines(self):
        with tmp_file_containing('') as file_path:
            ls = line_source.new_for_file(file_path)
            actual = list(iter(ls))
        self.assertEqual([], actual)

    def test_single_linesep_should_give_two_lines(self):
        two_lines = os.linesep.join(['first',
                                     'second'])
        with tmp_file_containing(two_lines) as file_path:
            ls = line_source.new_for_file(file_path)
            actual = list(iter(ls))
        expected = [line(1, 'first'),
                    line(2, 'second')]
        self.assertEqual(expected, actual)

    def test_trailing_linesep_should_produce_no_line(self):
        single_line_with_linesep = 'first' + os.linesep
        with tmp_file_containing(single_line_with_linesep) as file_path:
            ls = line_source.new_for_file(file_path)
            actual = list(iter(ls))
        expected = [line(1, 'first')]
        self.assertEqual(expected, actual)

    def test_empty_line(self):
        contents = 'first' + os.linesep + os.linesep
        with tmp_file_containing(contents) as file_path:
            ls = line_source.new_for_file(file_path)
            actual = list(iter(ls))
        expected = [line(1, 'first'),
                    line(2, '')]
        self.assertEqual(expected, actual)


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestStringLineSource))
    ret_val.addTest(unittest.makeSuite(TestFileLineSource))
    return ret_val


if __name__ == '__main__':
    unittest.main()
    unittest.main()
