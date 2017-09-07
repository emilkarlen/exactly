import unittest

from exactly_lib.test_case_utils.file_matcher import file_matchers
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.util.dir_contents_selection import Selectors
from exactly_lib_test.test_case_utils.file_matcher.test_resources import value_assertions as sut
from exactly_lib_test.test_resources.name_and_value import NameAndValue
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestEquals),
        unittest.makeSuite(TestNotEquals),
    ])


class TestEquals(unittest.TestCase):
    def test(self):
        # ARRANGE #
        cases = [
            (
                file_matchers.FileMatcherConstant(False),
                file_matchers.FileMatcherConstant(False),
            ),
            (
                file_matchers.FileMatcherConstant(True),
                file_matchers.FileMatcherConstant(True),
            ),
            (
                file_matchers.FileMatcherFromSelectors(Selectors()),
                file_matchers.FileMatcherFromSelectors(Selectors()),
            ),
            (
                file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['pattern']))),
                file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['pattern']))),
            ),
            (
                file_matchers.FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.REGULAR]))),
                file_matchers.FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.REGULAR]))),
            ),
            (
                file_matchers.FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.DIRECTORY]))),
                file_matchers.FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.DIRECTORY]))),
            ),
        ]
        for expected, actual in cases:
            with self.subTest(case_name=expected.option_description):
                assertion = sut.equals_file_matcher(expected)
                # ACT & ASSERT #
                assertion.apply_without_message(self, actual)


class TestNotEquals(unittest.TestCase):
    def test_selectors(self):
        # ARRANGE #
        expected = file_matchers.FileMatcherFromSelectors(Selectors())
        cases = [
            file_matchers.FileMatcherConstant(False),
            file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['pattern']))),
            file_matchers.FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.REGULAR]))),
        ]
        assertion_to_check = sut.equals_file_matcher(expected)
        for actual in cases:
            with self.subTest(name=actual.option_description):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_constant(self):
        # ARRANGE #
        expected = file_matchers.FileMatcherConstant(False)
        cases = [
            file_matchers.FileMatcherConstant(True),
            file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['pattern']))),
            file_matchers.FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.REGULAR]))),
        ]
        assertion_to_check = sut.equals_file_matcher(expected)
        for actual in cases:
            with self.subTest(name=actual.option_description):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_selectors__name_patterns(self):
        # ARRANGE #
        expected = file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['pattern 1',
                                                                                             'pattern 2'])))
        actual = file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['pattern 1',
                                                                                           'pattern 2'])))
        assertion = sut.equals_file_matcher(expected)
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_selectors__name_patterns(self):
        # ARRANGE #
        assertion_to_check = sut.equals_file_matcher(file_matchers.FileMatcherFromSelectors(Selectors(
            name_patterns=frozenset(['expected pattern'])
        )))
        cases = [
            NameAndValue('name pattern mismatch',
                         file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['actual pattern'])))
                         ),
            NameAndValue('one additional pattern',
                         file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['expected pattern',
                                                                                                   'actual pattern'])))
                         ),
            NameAndValue('file type mismatch',
                         file_matchers.FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.REGULAR])))
                         ),
            NameAndValue('empty selection',
                         file_matchers.FileMatcherFromSelectors(Selectors())
                         ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            case.value)

    def test_selectors__file_types(self):
        # ARRANGE #
        expected = file_matchers.FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.REGULAR,
                                                                                          FileType.SYMLINK])))
        actual = file_matchers.FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.REGULAR,
                                                                                        FileType.SYMLINK])))
        assertion = sut.equals_file_matcher(expected)
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_selectors__file_types(self):
        # ARRANGE #
        assertion_to_check = sut.equals_file_matcher(file_matchers.FileMatcherFromSelectors(Selectors(
            file_types=frozenset([FileType.SYMLINK,
                                  FileType.DIRECTORY])
        )))
        cases = [
            NameAndValue('name pattern mismatch',
                         file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['actual pattern'])))
                         ),
            NameAndValue('one additional pattern',
                         file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['expected pattern',
                                                                                                   'actual pattern'])))
                         ),
            NameAndValue('missing file type',
                         file_matchers.FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.DIRECTORY])))
                         ),
            NameAndValue('different file types',
                         file_matchers.FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.REGULAR,
                                                                                                FileType.DIRECTORY])))
                         ),
            NameAndValue('name pattern mismatch',
                         file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['actual pattern'])))
                         ),
            NameAndValue('empty selection',
                         file_matchers.FileMatcherFromSelectors(Selectors())
                         ),
        ]
        for case in cases:
            with self.subTest(name=case.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            case.value)

    def test_selectors__name_patterns_and_file_types(self):
        # ARRANGE #
        expected = file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['p']),
                                                                    file_types=frozenset([FileType.REGULAR])))
        actual = file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['p']),
                                                                  file_types=frozenset([FileType.REGULAR])))
        assertion = sut.equals_file_matcher(expected)
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
