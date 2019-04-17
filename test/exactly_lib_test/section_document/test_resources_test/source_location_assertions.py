import pathlib
import unittest

from exactly_lib.section_document.source_location import SourceLocationPath, source_location_path_without_inclusions, \
    SourceLocation
from exactly_lib.util.line_source import LineSequence
from exactly_lib_test.section_document.test_resources import source_location_assertions as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.util.test_resources.line_source_assertions import ARBITRARY_LINE_SEQUENCE


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEqualsSourceLocation),
        unittest.makeSuite(TestEqualsSourceLocationPath),
    ])


ARBITRARY_SOURCE_LOCATION_INFO = sut.SourceLocationInfo(
    pathlib.Path('abs_path_of_dir_containing_first_file_path'),
    SourceLocationPath(SourceLocation(ARBITRARY_LINE_SEQUENCE, None), [])
)


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
                assertion = sut.equals_source_location(
                    nea.expected)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion, nea.actual)

    def test_equals(self):
        assertion = sut.equals_source_location(
            SourceLocation(self.line_sequence_1, self.path_a))
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
                assertion = sut.equals_source_location_path(
                    nea.expected)
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
                assertion = sut.equals_source_location_path(
                    nea.expected)
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion, nea.actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
