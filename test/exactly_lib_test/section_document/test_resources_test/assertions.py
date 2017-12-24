import unittest

from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.section_document.test_resources import assertions as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsLineSequence),
    ])


class EA:
    """Expected and actual"""

    def __init__(self,
                 expected,
                 actual):
        self.expected = expected
        self.actual = actual


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
