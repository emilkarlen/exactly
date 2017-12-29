import pathlib
import unittest

from exactly_lib.util.line_source import LineSequence, Line, SourceLocation, SourceLocationPath, \
    source_location_path_without_inclusions
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.util.test_resources import line_source_assertions as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsLine),
        unittest.makeSuite(TestEqualsLineSequence),
        unittest.makeSuite(TestEqualsSourceLocation),
        unittest.makeSuite(TestEqualsSourceLocationPath),
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
            NEA('unequal line number',
                expected=Line(2, 'text'),
                actual=Line(1, 'text')
                ),
            NEA('unequal text',
                expected=Line(1, 'expected'),
                actual=Line(1, 'actual')
                ),
        ]

        for name_and_ea in cases:
            with self.subTest(name_and_ea.name):
                assertion = sut.equals_line(name_and_ea.expected)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion, name_and_ea.actual)


class TestEqualsLineSequence(unittest.TestCase):
    def test_SHOULD_be_equal(self):
        # ARRANGE #
        cases = [
            NEA('without lines',
                expected=LineSequence(1, ()),
                actual=LineSequence(1, ())
                ),
            NEA('with lines',
                expected=LineSequence(2, ('first', 'second')),
                actual=LineSequence(2, ('first', 'second'))
                ),
        ]

        for name_and_ea in cases:
            with self.subTest(name_and_ea.name):
                assertion = sut.equals_line_sequence(name_and_ea.expected)
                # ACT & ASSERT #
                assertion.apply_without_message(self, name_and_ea.actual)

    def test_SHOULD_not_be_equal(self):
        # ARRANGE #
        cases = [
            NEA('unequal first line',
                expected=LineSequence(1, ()),
                actual=LineSequence(2, ())),
            NEA('unequal single line',
                expected=LineSequence(1, ('expected',)),
                actual=LineSequence(1, ('actual',))),
            NEA('unequal number of lines',
                expected=LineSequence(1, ('line', 'line')),
                actual=LineSequence(1, ('line',))),
        ]

        for name_and_ea in cases:
            with self.subTest(name_and_ea.name):
                assertion = sut.equals_line_sequence(name_and_ea.expected)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion, name_and_ea.actual)


class TestEqualsSourceLocation(unittest.TestCase):
    path_a = pathlib.Path('a')
    path_b = pathlib.Path('b')

    line_sequence_1 = LineSequence(1, ['line'])
    line_sequence_2 = LineSequence(2, ['line'])

    def test_not_equals(self):
        cases = [
            NEA('different path',
                SourceLocation(self.line_sequence_1, self.path_a),
                SourceLocation(self.line_sequence_1, self.path_b),
                ),
            NEA('different line sequence',
                SourceLocation(self.line_sequence_1, self.path_a),
                SourceLocation(self.line_sequence_2, self.path_a),
                ),
        ]
        for nea in cases:
            with self.subTest(nea.name):
                assertion = sut.equals_source_location(nea.expected)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion, nea.actual)

    def test_equals(self):
        assertion = sut.equals_source_location(SourceLocation(self.line_sequence_1, self.path_a))
        # ACT & ASSERT #
        assertion.apply_without_message(self, SourceLocation(self.line_sequence_1, self.path_a))


class TestEqualsSourceLocationPath(unittest.TestCase):
    path_a = pathlib.Path('a')
    path_b = pathlib.Path('b')

    line_sequence_1 = LineSequence(1, ['line'])
    line_sequence_2 = LineSequence(2, ['line'])

    def test_equals(self):
        location1 = SourceLocation(self.line_sequence_1, self.path_a)
        location2 = SourceLocation(self.line_sequence_2, self.path_b)
        cases = [
            NEA('without file inclusion chain',
                expected=source_location_path_without_inclusions(location1),
                actual=source_location_path_without_inclusions(location1),
                ),
            NEA('with file inclusion chain',
                expected=SourceLocationPath(location2, [location1]),
                actual=SourceLocationPath(location2, [location1]),
                ),
        ]
        for nea in cases:
            with self.subTest(nea.name):
                assertion = sut.equals_source_location_path(nea.expected)
                # ACT & ASSERT #
                assertion.apply_without_message(self, nea.actual)

    def test_not_equals(self):
        location1 = SourceLocation(self.line_sequence_1, self.path_a)
        location2 = SourceLocation(self.line_sequence_2, self.path_b)

        cases = [
            NEA('without inclusion chain/different location',
                expected=source_location_path_without_inclusions(location1),
                actual=source_location_path_without_inclusions(location2),
                ),
            NEA('with inclusion chain/different location',
                expected=SourceLocationPath(location1, [location1]),
                actual=SourceLocationPath(location2, [location1]),
                ),
            NEA('different inclusion chain / different size',
                expected=SourceLocationPath(location1, [location1]),
                actual=SourceLocationPath(location1, []),
                ),
            NEA('different inclusion chain / different contents',
                expected=SourceLocationPath(location1, [location1]),
                actual=SourceLocationPath(location1, [location2]),
                ),
        ]
        for nea in cases:
            with self.subTest(nea.name):
                assertion = sut.equals_source_location_path(nea.expected)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion, nea.actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
