import re
import unittest

from exactly_lib.test_case_utils.file_matcher import file_matchers
from exactly_lib.test_case_utils.file_matcher.impl import combinators
from exactly_lib.test_case_utils.file_matcher.impl.file_type import FileMatcherType
from exactly_lib.test_case_utils.file_matcher.impl.name_glob_pattern import FileMatcherNameGlobPattern
from exactly_lib.test_case_utils.file_matcher.impl.name_regex import FileMatcherBaseNameRegExPattern
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
                FileMatcherNameGlobPattern('glob pattern'),
                FileMatcherNameGlobPattern('glob pattern'),
            ),
            (
                FileMatcherBaseNameRegExPattern(re.compile('reg-ex pattern')),
                FileMatcherBaseNameRegExPattern(re.compile('reg-ex pattern')),
            ),
            (
                FileMatcherType(FileType.DIRECTORY),
                FileMatcherType(FileType.DIRECTORY),
            ),
            (
                combinators.FileMatcherNot(file_matchers.FileMatcherConstant(True)),
                combinators.FileMatcherNot(file_matchers.FileMatcherConstant(True)),
            ),
            (
                combinators.FileMatcherAnd([]),
                combinators.FileMatcherAnd([]),
            ),
            (
                combinators.FileMatcherAnd([file_matchers.FileMatcherConstant(True)]),
                combinators.FileMatcherAnd([file_matchers.FileMatcherConstant(True)]),
            ),
            (
                combinators.FileMatcherOr([]),
                combinators.FileMatcherOr([]),
            ),
            (
                combinators.FileMatcherOr([file_matchers.FileMatcherConstant(False)]),
                combinators.FileMatcherOr([file_matchers.FileMatcherConstant(False)]),
            ),
            (
                combinators.FileMatcherAnd([file_matchers.FileMatcherConstant(False)]),
                combinators.FileMatcherAnd([file_matchers.FileMatcherConstant(False)]),
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
        expected = FileMatcherNameGlobPattern('expected glob pattern')
        cases = [
            FileMatcherNameGlobPattern('actual glob pattern'),
            FileMatcherBaseNameRegExPattern(re.compile('reg-ex pattern')),
            file_matchers.FileMatcherConstant(False),
            FileMatcherType(FileType.REGULAR),
            combinators.FileMatcherNot(file_matchers.FileMatcherConstant(True)),
            combinators.FileMatcherAnd([]),
            combinators.FileMatcherOr([]),
            combinators.FileMatcherOr([file_matchers.FileMatcherConstant(False)]),
        ]
        assertion_to_check = sut.equals_file_matcher(expected)
        for actual in cases:
            with self.subTest(name=actual.option_description):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_name_reg_ex_pattern(self):
        # ARRANGE #
        expected = FileMatcherBaseNameRegExPattern(re.compile('expected reg-ex pattern'))
        cases = [
            FileMatcherNameGlobPattern('actual glob pattern'),
            FileMatcherBaseNameRegExPattern(re.compile('actual reg-ex pattern')),
            file_matchers.FileMatcherConstant(False),
            FileMatcherType(FileType.REGULAR),
            combinators.FileMatcherNot(file_matchers.FileMatcherConstant(True)),
            combinators.FileMatcherAnd([]),
            combinators.FileMatcherOr([]),
            combinators.FileMatcherOr([file_matchers.FileMatcherConstant(False)]),
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
            FileMatcherNameGlobPattern('glob pattern'),
            FileMatcherBaseNameRegExPattern(re.compile('reg-ex pattern')),
            FileMatcherType(FileType.REGULAR),
            combinators.FileMatcherNot(file_matchers.FileMatcherConstant(True)),
            combinators.FileMatcherAnd([]),
            combinators.FileMatcherOr([]),
            combinators.FileMatcherOr([file_matchers.FileMatcherConstant(False)]),
        ]
        assertion_to_check = sut.equals_file_matcher(expected)
        for actual in cases:
            with self.subTest(name=actual.option_description):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_file_types(self):
        # ARRANGE #
        assertion_to_check = sut.equals_file_matcher(
            FileMatcherType(FileType.SYMLINK))

        actual_matchers = [
            FileMatcherType(FileType.REGULAR),
            FileMatcherNameGlobPattern('glob pattern'),
            FileMatcherBaseNameRegExPattern(re.compile('reg-ex pattern')),
            file_matchers.FileMatcherConstant(True),
            combinators.FileMatcherNot(file_matchers.FileMatcherConstant(True)),
            combinators.FileMatcherAnd([]),
            combinators.FileMatcherOr([]),
            combinators.FileMatcherOr([file_matchers.FileMatcherConstant(False)]),
        ]
        for actual in actual_matchers:
            with self.subTest(name=actual.option_description):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_not(self):
        # ARRANGE #
        expected = combinators.FileMatcherNot(file_matchers.FileMatcherConstant(True))
        cases = [
            combinators.FileMatcherNot(file_matchers.FileMatcherConstant(False)),
            combinators.FileMatcherAnd([file_matchers.FileMatcherConstant(False)]),
            combinators.FileMatcherAnd([]),
            file_matchers.FileMatcherConstant(True),
            FileMatcherNameGlobPattern('glob pattern'),
            FileMatcherBaseNameRegExPattern(re.compile('reg-ex pattern')),
            FileMatcherType(FileType.REGULAR),
            combinators.FileMatcherOr([]),
            combinators.FileMatcherOr([file_matchers.FileMatcherConstant(False)]),
        ]
        assertion_to_check = sut.equals_file_matcher(expected)
        for actual in cases:
            with self.subTest(name=actual.option_description):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_and(self):
        # ARRANGE #
        expected = combinators.FileMatcherAnd([file_matchers.FileMatcherConstant(True)])
        cases = [
            combinators.FileMatcherAnd([file_matchers.FileMatcherConstant(False)]),
            combinators.FileMatcherAnd([]),
            file_matchers.FileMatcherConstant(True),
            FileMatcherNameGlobPattern('glob pattern'),
            FileMatcherBaseNameRegExPattern(re.compile('reg-ex pattern')),
            FileMatcherType(FileType.REGULAR),
            combinators.FileMatcherNot(file_matchers.FileMatcherConstant(True)),
            combinators.FileMatcherOr([]),
            combinators.FileMatcherOr([file_matchers.FileMatcherConstant(False)]),
        ]
        assertion_to_check = sut.equals_file_matcher(expected)
        for actual in cases:
            with self.subTest(name=actual.option_description):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)

    def test_or(self):
        # ARRANGE #
        expected = combinators.FileMatcherOr([file_matchers.FileMatcherConstant(True)])
        cases = [
            combinators.FileMatcherOr([file_matchers.FileMatcherConstant(False)]),
            combinators.FileMatcherOr([]),
            file_matchers.FileMatcherConstant(True),
            FileMatcherNameGlobPattern('glob pattern'),
            FileMatcherBaseNameRegExPattern(re.compile('reg-ex pattern')),
            FileMatcherType(FileType.REGULAR),
            combinators.FileMatcherNot(file_matchers.FileMatcherConstant(True)),
            combinators.FileMatcherAnd([]),
            combinators.FileMatcherAnd([file_matchers.FileMatcherConstant(False)]),
        ]
        assertion_to_check = sut.equals_file_matcher(expected)
        for actual in cases:
            with self.subTest(name=actual.option_description):
                # ACT & ASSERT #
                assert_that_assertion_fails(assertion_to_check,
                                            actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
