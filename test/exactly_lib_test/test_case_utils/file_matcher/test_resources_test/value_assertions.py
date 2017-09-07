import unittest

from exactly_lib.test_case_utils.file_matcher import file_matchers
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.util.dir_contents_selection import Selectors
from exactly_lib_test.test_case_utils.file_matcher.test_resources import value_assertions as sut
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
                file_matchers.FileMatcherNameGlobPattern('glob pattern'),
                file_matchers.FileMatcherNameGlobPattern('glob pattern'),
            ),
            (
                file_matchers.FileMatcherType(FileType.DIRECTORY),
                file_matchers.FileMatcherType(FileType.DIRECTORY),
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
    def test_name_glob_pattern(self):
        # ARRANGE #
        expected = file_matchers.FileMatcherNameGlobPattern('expected glob pattern')
        cases = [
            file_matchers.FileMatcherNameGlobPattern('actual glob pattern'),
            file_matchers.FileMatcherConstant(False),
            file_matchers.FileMatcherType(FileType.REGULAR),
            file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['pattern']))),
            file_matchers.FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.REGULAR]))),
        ]
        assertion_to_check = sut.equals_file_matcher(expected)
        for actual in cases:
            with self.subTest(name=actual.option_description):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_selectors(self):
        # ARRANGE #
        expected = file_matchers.FileMatcherFromSelectors(Selectors())
        cases = [
            file_matchers.FileMatcherConstant(False),
            file_matchers.FileMatcherNameGlobPattern('glob pattern'),
            file_matchers.FileMatcherType(FileType.REGULAR),
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
            file_matchers.FileMatcherNameGlobPattern('glob pattern'),
            file_matchers.FileMatcherType(FileType.REGULAR),
            file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['pattern']))),
            file_matchers.FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.REGULAR]))),
        ]
        assertion_to_check = sut.equals_file_matcher(expected)
        for actual in cases:
            with self.subTest(name=actual.option_description):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_file_types(self):
        # ARRANGE #
        assertion_to_check = sut.equals_file_matcher(file_matchers.FileMatcherType(FileType.SYMLINK))

        actual_matchers = [
            file_matchers.FileMatcherType(FileType.REGULAR),
            file_matchers.FileMatcherNameGlobPattern('glob pattern'),
            file_matchers.FileMatcherConstant(True),
            file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['actual pattern']))),
            file_matchers.FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.DIRECTORY]))),
            file_matchers.FileMatcherFromSelectors(Selectors()),
        ]
        for actual in actual_matchers:
            with self.subTest(name=actual.option_description):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_selectors__name_patterns(self):
        # ARRANGE #
        assertion_to_check = sut.equals_file_matcher(file_matchers.FileMatcherFromSelectors(Selectors(
            name_patterns=frozenset(['expected pattern'])
        )))
        actual_matchers = [
            file_matchers.FileMatcherConstant(True),
            file_matchers.FileMatcherNameGlobPattern('glob pattern'),
            file_matchers.FileMatcherType(FileType.REGULAR),
            file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['actual pattern']))),
            file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['expected pattern',
                                                                                      'actual pattern']))),
            file_matchers.FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.REGULAR]))),
            file_matchers.FileMatcherFromSelectors(Selectors()),
        ]
        for actual in actual_matchers:
            with self.subTest(name=actual.option_description):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_selectors__file_types(self):
        # ARRANGE #
        assertion_to_check = sut.equals_file_matcher(file_matchers.FileMatcherFromSelectors(Selectors(
            file_types=frozenset([FileType.SYMLINK,
                                  FileType.DIRECTORY])
        )))
        actual_matchers = [
            file_matchers.FileMatcherConstant(True),
            file_matchers.FileMatcherNameGlobPattern('glob pattern'),
            file_matchers.FileMatcherType(FileType.REGULAR),
            file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['actual pattern']))),
            file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['expected pattern',
                                                                                      'actual pattern']))),
            file_matchers.FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.DIRECTORY]))),
            file_matchers.FileMatcherFromSelectors(Selectors(file_types=frozenset([FileType.REGULAR,
                                                                                   FileType.DIRECTORY]))),
            file_matchers.FileMatcherFromSelectors(Selectors(name_patterns=frozenset(['actual pattern']))),
            file_matchers.FileMatcherFromSelectors(Selectors()),
        ]
        for actual in actual_matchers:
            with self.subTest(name=actual.option_description):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

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
