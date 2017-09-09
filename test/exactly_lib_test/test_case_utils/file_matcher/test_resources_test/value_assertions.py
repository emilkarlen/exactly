import unittest

from exactly_lib.test_case_utils.file_matcher import file_matchers
from exactly_lib.test_case_utils.file_properties import FileType
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
                file_matchers.FileMatcherNot(file_matchers.FileMatcherConstant(True)),
                file_matchers.FileMatcherNot(file_matchers.FileMatcherConstant(True)),
            ),
            (
                file_matchers.FileMatcherAnd([]),
                file_matchers.FileMatcherAnd([]),
            ),
            (
                file_matchers.FileMatcherAnd([file_matchers.FileMatcherConstant(True)]),
                file_matchers.FileMatcherAnd([file_matchers.FileMatcherConstant(True)]),
            ),
            (
                file_matchers.FileMatcherOr([]),
                file_matchers.FileMatcherOr([]),
            ),
            (
                file_matchers.FileMatcherOr([file_matchers.FileMatcherConstant(False)]),
                file_matchers.FileMatcherOr([file_matchers.FileMatcherConstant(False)]),
            ),
            (
                file_matchers.FileMatcherAnd([file_matchers.FileMatcherConstant(False)]),
                file_matchers.FileMatcherAnd([file_matchers.FileMatcherConstant(False)]),
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
            file_matchers.FileMatcherNot(file_matchers.FileMatcherConstant(True)),
            file_matchers.FileMatcherAnd([]),
            file_matchers.FileMatcherOr([]),
            file_matchers.FileMatcherOr([file_matchers.FileMatcherConstant(False)]),
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
            file_matchers.FileMatcherNot(file_matchers.FileMatcherConstant(True)),
            file_matchers.FileMatcherAnd([]),
            file_matchers.FileMatcherOr([]),
            file_matchers.FileMatcherOr([file_matchers.FileMatcherConstant(False)]),
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
            file_matchers.FileMatcherNot(file_matchers.FileMatcherConstant(True)),
            file_matchers.FileMatcherAnd([]),
            file_matchers.FileMatcherOr([]),
            file_matchers.FileMatcherOr([file_matchers.FileMatcherConstant(False)]),
        ]
        for actual in actual_matchers:
            with self.subTest(name=actual.option_description):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_not(self):
        # ARRANGE #
        expected = file_matchers.FileMatcherNot(file_matchers.FileMatcherConstant(True))
        cases = [
            file_matchers.FileMatcherNot(file_matchers.FileMatcherConstant(False)),
            file_matchers.FileMatcherAnd([file_matchers.FileMatcherConstant(False)]),
            file_matchers.FileMatcherAnd([]),
            file_matchers.FileMatcherConstant(True),
            file_matchers.FileMatcherNameGlobPattern('glob pattern'),
            file_matchers.FileMatcherType(FileType.REGULAR),
            file_matchers.FileMatcherOr([]),
            file_matchers.FileMatcherOr([file_matchers.FileMatcherConstant(False)]),
        ]
        assertion_to_check = sut.equals_file_matcher(expected)
        for actual in cases:
            with self.subTest(name=actual.option_description):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_and(self):
        # ARRANGE #
        expected = file_matchers.FileMatcherAnd([file_matchers.FileMatcherConstant(True)])
        cases = [
            file_matchers.FileMatcherAnd([file_matchers.FileMatcherConstant(False)]),
            file_matchers.FileMatcherAnd([]),
            file_matchers.FileMatcherConstant(True),
            file_matchers.FileMatcherNameGlobPattern('glob pattern'),
            file_matchers.FileMatcherType(FileType.REGULAR),
            file_matchers.FileMatcherNot(file_matchers.FileMatcherConstant(True)),
            file_matchers.FileMatcherOr([]),
            file_matchers.FileMatcherOr([file_matchers.FileMatcherConstant(False)]),
        ]
        assertion_to_check = sut.equals_file_matcher(expected)
        for actual in cases:
            with self.subTest(name=actual.option_description):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_or(self):
        # ARRANGE #
        expected = file_matchers.FileMatcherOr([file_matchers.FileMatcherConstant(True)])
        cases = [
            file_matchers.FileMatcherOr([file_matchers.FileMatcherConstant(False)]),
            file_matchers.FileMatcherOr([]),
            file_matchers.FileMatcherConstant(True),
            file_matchers.FileMatcherNameGlobPattern('glob pattern'),
            file_matchers.FileMatcherType(FileType.REGULAR),
            file_matchers.FileMatcherNot(file_matchers.FileMatcherConstant(True)),
            file_matchers.FileMatcherAnd([]),
            file_matchers.FileMatcherAnd([file_matchers.FileMatcherConstant(False)]),
        ]
        assertion_to_check = sut.equals_file_matcher(expected)
        for actual in cases:
            with self.subTest(name=actual.option_description):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
