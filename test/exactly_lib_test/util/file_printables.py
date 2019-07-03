import os
import unittest

from exactly_lib.util import file_printables as sut
from exactly_lib_test.test_resources.test_utils import NEA


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestToStringUndoesFromString),  # This test is a prerequisite for the other tests
        unittest.makeSuite(TestSimple),
        unittest.makeSuite(TestComplex),
    ])


class TestToStringUndoesFromString(unittest.TestCase):
    def test(self):
        # ARRANGE #
        cases = [
            '',
            'word',
            'word1 word2',
            'text with \n embedded',
        ]
        for expected in cases:
            with self.subTest(expected):
                # ACT #
                file_printable = sut.of_constant_string(expected)
                actual = sut.print_to_string(file_printable)
                # ASSERT #
                self.assertEqual(expected, actual)


class TestSimple(unittest.TestCase):
    def test_newline(self):
        # ACT #
        file_printable = sut.of_new_line()
        actual = sut.print_to_string(file_printable)
        # ASSERT #
        self.assertEqual(os.linesep, actual)

    def test_format_string(self):
        # ARRANGE #
        format_map = {
            'a': 'A',
            'b': 'bb',
        }
        format_string = 'First {a} then {b}'
        expected = format_string.format_map(format_map)
        # ACT #
        file_printable = sut.of_format_string(format_string, format_map)
        actual = sut.print_to_string(file_printable)
        # ASSERT #
        self.assertEqual(expected, actual)

    def test_format_string_args(self):
        # ARRANGE #
        format_args = (
            'A',
            'bb',
        )
        format_string = 'First {} then {}'
        expected = format_string.format(*format_args)
        # ACT #
        file_printable = sut.of_format_string_args(format_string, *format_args)
        actual = sut.print_to_string(file_printable)
        # ASSERT #
        self.assertEqual(expected, actual)


class TestComplex(unittest.TestCase):
    def test_sequence(self):
        cases = [
            NEA('empty',
                '',
                []
                ),
            NEA('singleton',
                'single',
                [sut.of_constant_string('single')]
                ),
            NEA('multiple',
                '1st2nd',
                [sut.of_constant_string('1st'),
                 sut.of_constant_string('2nd')]),
        ]
        for case in cases:
            with self.subTest(case.name):
                file_printer = sut.of_sequence(case.actual)
                # ACT #
                actual = sut.print_to_string(file_printer)
                # ASSERT #
                self.assertEqual(case.expected, actual)

    def test_newline_ended_sequence(self):
        cases = [
            NEA('empty',
                '' + os.linesep,
                []
                ),
            NEA('singleton',
                'single' + os.linesep,
                [sut.of_constant_string('single')]
                ),
            NEA('multiple',
                '1st2nd' + os.linesep,
                [sut.of_constant_string('1st'),
                 sut.of_constant_string('2nd')]),
        ]
        for case in cases:
            with self.subTest(case.name):
                file_printer = sut.of_newline_ended_sequence(case.actual)
                # ACT #
                actual = sut.print_to_string(file_printer)
                # ASSERT #
                self.assertEqual(case.expected, actual)

    def test_newline_ended_items(self):
        cases = [
            NEA('empty',
                '',
                []
                ),
            NEA('singleton',
                'single' + os.linesep,
                [sut.of_constant_string('single')]
                ),
            NEA('multiple',
                '1st' + os.linesep + '2nd' + os.linesep,
                [sut.of_constant_string('1st'),
                 sut.of_constant_string('2nd')]),
        ]
        for case in cases:
            with self.subTest(case.name):
                file_printer = sut.of_newline_ended_items(case.actual)
                # ACT #
                actual = sut.print_to_string(file_printer)
                # ASSERT #
                self.assertEqual(case.expected, actual)

    def test_newline_separated_items(self):
        cases = [
            NEA('empty',
                '',
                []
                ),
            NEA('singleton',
                'single',
                [sut.of_constant_string('single')]
                ),
            NEA('multiple',
                '1st' + os.linesep + '2nd',
                [sut.of_constant_string('1st'),
                 sut.of_constant_string('2nd')]),
        ]
        for case in cases:
            with self.subTest(case.name):
                file_printer = sut.of_newline_separated_items(case.actual)
                # ACT #
                actual = sut.print_to_string(file_printer)
                # ASSERT #
                self.assertEqual(case.expected, actual)
