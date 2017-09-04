import unittest

from exactly_lib.test_case_utils.file_matcher.file_matchers import FileMatcherFromSelectors
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.util.dir_contents_selection import Selectors
from exactly_lib_test.test_case_utils.file_matcher.test_resources import value_assertions as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestEqualsFileMatcher)


class TestEqualsFileMatcher(unittest.TestCase):
    def test_equals_empty(self):
        # ARRANGE #
        expected = FileMatcherFromSelectors(Selectors())
        actual = FileMatcherFromSelectors(Selectors())
        assertion = sut.equals_file_matcher(expected)
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_not_equals_empty(self):
        # ARRANGE #
        cases = [
            NameAndValue('name pattern mismatch',
                         FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['pattern'])))
                         ),
            NameAndValue('file type mismatch',
                         FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.REGULAR])))
                         ),
        ]
        assertion_to_check = sut.equals_file_matcher(FileMatcherFromSelectors(Selectors()))
        for case in cases:
            with self.subTest(name=case.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            case.value)

    def test_equals_name_patterns(self):
        # ARRANGE #
        expected = FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['pattern 1',
                                                                               'pattern 2'])))
        actual = FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['pattern 1',
                                                                             'pattern 2'])))
        assertion = sut.equals_file_matcher(expected)
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_not_equals_name_patterns(self):
        # ARRANGE #
        assertion_to_check = sut.equals_file_matcher(FileMatcherFromSelectors(Selectors(
            name_patterns=frozenset(['expected pattern'])
        )))
        cases = [
            NameAndValue('name pattern mismatch',
                         FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['actual pattern'])))
                         ),
            NameAndValue('one additional pattern',
                         FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['expected pattern',
                                                                                     'actual pattern'])))
                         ),
            NameAndValue('file type mismatch',
                         FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.REGULAR])))
                         ),
            NameAndValue('empty selection',
                         FileMatcherFromSelectors(Selectors())
                         ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            case.value)

    def test_equals_file_types(self):
        # ARRANGE #
        expected = FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.REGULAR,
                                                                            FileType.SYMLINK])))
        actual = FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.REGULAR,
                                                                          FileType.SYMLINK])))
        assertion = sut.equals_file_matcher(expected)
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_not_equals_file_types(self):
        # ARRANGE #
        assertion_to_check = sut.equals_file_matcher(FileMatcherFromSelectors(Selectors(
            file_types=frozenset([FileType.SYMLINK,
                                  FileType.DIRECTORY])
        )))
        cases = [
            NameAndValue('name pattern mismatch',
                         FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['actual pattern'])))
                         ),
            NameAndValue('one additional pattern',
                         FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['expected pattern',
                                                                                     'actual pattern'])))
                         ),
            NameAndValue('missing file type',
                         FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.DIRECTORY])))
                         ),
            NameAndValue('different file types',
                         FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.REGULAR,
                                                                                  FileType.DIRECTORY])))
                         ),
            NameAndValue('name pattern mismatch',
                         FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['actual pattern'])))
                         ),
            NameAndValue('empty selection',
                         FileMatcherFromSelectors(Selectors())
                         ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            case.value)

    def test_equals_name_patterns_and_file_types(self):
        # ARRANGE #
        expected = FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['p']),
                                                      file_types=frozenset([FileType.REGULAR])))
        actual = FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['p']),
                                                    file_types=frozenset([FileType.REGULAR])))
        assertion = sut.equals_file_matcher(expected)
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
