import unittest

from exactly_lib.util.line_source import LineSequence, Line
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import EA
from exactly_lib_test.util.test_resources import line_source_assertions as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsLine),
        unittest.makeSuite(TestEqualsLineSequence),
    ])


class TestEqualsLine(unittest.TestCase):
    def test_SHOULD_be_equal(self):
        # ARRANGE #
        expected = Line(1, 'text')
        actual = Line(1, 'text')
        assertion = sut.equals_line(expected)
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_SHOULD_not_be_equal(self):
        # ARRANGE #
        cases = [
            NameAndValue('unequal line number',
                         EA(expected=Line(2, 'text'),
                            actual=Line(1, 'text'))
                         ),
            NameAndValue('unequal text',
                         EA(expected=Line(1, 'expected'),
                            actual=Line(1, 'actual'))
                         ),
        ]

        for name_and_ea in cases:
            with self.subTest(name_and_ea.name):
                assertion = sut.equals_line(name_and_ea.value.expected)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion, name_and_ea.value.actual)


class TestEqualsLineSequence(unittest.TestCase):
    def test_SHOULD_be_equal(self):
        # ARRANGE #
        cases = [
            NameAndValue('without lines',
                         EA(expected=LineSequence(1, ()),
                            actual=LineSequence(1, ()))),
            NameAndValue('with lines',
                         EA(expected=LineSequence(2, ('first', 'second')),
                            actual=LineSequence(2, ('first', 'second')))),
        ]

        for name_and_ea in cases:
            with self.subTest(name_and_ea.name):
                assertion = sut.equals_line_sequence(name_and_ea.value.expected)
                # ACT & ASSERT #
                assertion.apply_without_message(self, name_and_ea.value.actual)

    def test_SHOULD_not_be_equal(self):
        # ARRANGE #
        cases = [
            NameAndValue('unequal first line',
                         EA(expected=LineSequence(1, ()),
                            actual=LineSequence(2, ()))),
            NameAndValue('unequal single line',
                         EA(expected=LineSequence(1, ('expected',)),
                            actual=LineSequence(1, ('actual',)))),
            NameAndValue('unequal number of lines',
                         EA(expected=LineSequence(1, ('line', 'line')),
                            actual=LineSequence(1, ('line',)))),
        ]

        for name_and_ea in cases:
            with self.subTest(name_and_ea.name):
                assertion = sut.equals_line_sequence(name_and_ea.value.expected)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion, name_and_ea.value.actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
