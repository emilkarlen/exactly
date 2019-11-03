import re
import unittest

from exactly_lib.test_case_utils.file_matcher.impl.file_type import FileMatcherType
from exactly_lib.test_case_utils.file_matcher.impl.name_glob_pattern import FileMatcherNameGlobPattern
from exactly_lib.test_case_utils.file_matcher.impl.name_regex import FileMatcherBaseNameRegExPattern
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib_test.test_case_utils.file_matcher.test_resources import value_assertions as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import assert_that_assertion_fails
from exactly_lib_test.test_resources.test_utils import NEA
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIsFileType),
        unittest.makeSuite(TestIsNameGlobPattern),
        unittest.makeSuite(TestIsBaseNameRegEx),
    ])


class TestIsFileType(unittest.TestCase):
    def test_matches(self):
        # ARRANGE #
        actual = FileMatcherType(FileType.DIRECTORY)
        assertion = sut.is_type_matcher(actual.file_type)
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_not_matches(self):
        # ARRANGE #
        cases = [
            NEA(
                'unexpected file type',
                sut.is_type_matcher(FileType.DIRECTORY),
                FileMatcherType(FileType.REGULAR),
            ),
            NEA(
                'unexpected matcher type',
                sut.is_type_matcher(FileType.DIRECTORY),
                FileMatcherNameGlobPattern('glob pattern'),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(case.expected,
                                            case.actual)


class TestIsNameGlobPattern(unittest.TestCase):
    def test_matches(self):
        # ARRANGE #
        actual = FileMatcherNameGlobPattern('*')
        assertion = sut.is_name_glob_pattern(asrt.equals(actual.glob_pattern))
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_not_matches(self):
        # ARRANGE #
        cases = [
            NEA(
                'unexpected pattern',
                sut.is_name_glob_pattern(asrt.equals('expected pattern')),
                FileMatcherNameGlobPattern('actual pattern'),
            ),
            NEA(
                'unexpected matcher type',
                sut.is_name_glob_pattern(asrt.anything_goes()),
                FileMatcherBaseNameRegExPattern(re.compile('reg-ex pattern')),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(case.expected,
                                            case.actual)


class TestIsBaseNameRegEx(unittest.TestCase):
    def test_matches(self):
        # ARRANGE #
        actual = FileMatcherBaseNameRegExPattern(re.compile('reg-ex pattern'))
        assertion = sut.is_name_regex(asrt.equals(actual.reg_ex_pattern))
        # ACT & ASSERT #
        assertion.apply_without_message(self, actual)

    def test_not_matches(self):
        # ARRANGE #
        cases = [
            NEA(
                'unexpected pattern',
                sut.is_name_regex(asrt.equals('expected pattern')),
                FileMatcherBaseNameRegExPattern(re.compile('actual pattern')),
            ),
            NEA(
                'unexpected matcher type',
                sut.is_name_regex(asrt.anything_goes()),
                FileMatcherNameGlobPattern('glob pattern'),
            ),
        ]
        for case in cases:
            with self.subTest(case.name):
                # ACT & ASSERT #
                assert_that_assertion_fails(case.expected,
                                            case.actual)


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
